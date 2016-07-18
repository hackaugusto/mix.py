// vim: set sts=4 sw=4 ts=4 et:

// Python.h includes pyconfig.h that unconditionally defines the
// _POSIX_C_SOURCE and other constants, since the extension is compiled with
// -Werror the compilation fail if Python.h is included after any system level
// header
#include <Python.h>

#include <signal.h>
#include <boost/python.hpp>
#include <boost/context/all.hpp>

namespace py = boost::python;
namespace ctx = boost::context;

/**
 * This is a implementation of cooperatively scheduled M:1 fibers for python,
 * the motivation for this project is to have the equivalent semantics as
 * greenlets but with no copying of the stack data.
 *
 * The initial ideia was to use UNIX's makecontext() family of functions, this
 * idea was dropped because the signal mask requires SYSCALLs to update the
 * current thread mask.
 *
 * The second idea was to roll a special implementation, based on
 * PTH/greenlet/Boost, but since the Boost implementation is OK I decided to
 * use it directly.
 *
 * Boost has a context library and a coroutine library, currently only the
 * context library is being used for simplicity.
 **/

/**
 * Some notes:
 *
 * mix does not keep track of a hierarchy of execution like the greenlet
 * library, this logic should be emulated in python.
 *
 * Currently there is no support for spagetthi/segmented stacks.
 *
 * We dont use the Python's TLS dictionary, the reason is that we don't wan't
 * to control if the fiber runs on another threads and don't want to worry
 * about the interpreter switchin threads under our feet (this happens with
 * greenlet because it calls interpreter code GetAttr and SetString)
 *
 * This implementation and greenlets are not thread-safe.
 *
 * TODO:
 *  - create another module that uses thread_local to store the main fiber
 **/

// FORWARD DECLARATIONS

// _Py_IDENTIFIER is not defined on python2.7
#if PY_MAJOR_VERSION >= 3
    _Py_IDENTIFIER(stdout);
    _Py_IDENTIFIER(stderr);
    _Py_IDENTIFIER(flush);
#endif

void first_call(intptr_t arguments_ptr);

// the first function called on a new stack
typedef struct {
    PyObject* callback;
    PyObject* args;
    PyObject* kwds;
} callback_t;

typedef struct {
    PyObject* args;
    PyObject* kwds;
} arguments_t;

typedef PyObject* result_t;

struct Fiber
{
    void* block;
    // the Fiber is primed if it is running, the first frame will call a python
    // callback or we left a running thread
    bool primed;
    std::size_t size;
    ctx::fcontext_t execution_context;
    py::object callback;
    py::object fls;

    Fiber(py::object callback) : Fiber(callback, SIGSTKSZ) {}

    Fiber(py::object callback, std::size_t size) :
        primed(false),
        size(size),
        callback(callback)
    {
        if (!PyCallable_Check(callback.ptr())) {
            PyErr_Format(PyExc_ValueError, "Fiber(): callback must be a callable");
            py::throw_error_already_set();
        }

        uintptr_t stack_top;

        block = PyMem_Malloc(size);

        // TODO: define per the direction that the stack grows
        stack_top = (uintptr_t)block;
        stack_top += size;

        fls = py::dict();

        execution_context = ctx::make_fcontext(
            (void*)stack_top,
            size,
            first_call
        );
    }

    ~Fiber() {
        // decrement the fls, it's okay if the fls is not deallocated because
        // it's storage is not part of the block/stack
        Py_DECREF(fls.ptr());
        PyMem_Free(block);
    }
};

/**
 * This function works as a trampoline and it will be called on the first jump,
 * it unwraps the python arguments and calls the python callable.
 **/
void first_call(intptr_t arguments_ptr) {
    callback_t *callback;
    PyObject* fiber;

    callback = (callback_t*)arguments_ptr;

    // PyObject_Call call will create a new frame object that will keep the
    // variables alive, we don't need to increase the refcount
    fiber = PyObject_Call(callback->callback, callback->args, callback->kwds);
    // If we get here either the function returned or a exception was raised
    // and not handled

    // The fiber needs to exit to guarantee proper cleanup, otherwise callback
    // could have references and keep objects alive.
    if (fiber) {
        // TODO: check the type of fiber and switch context
    }

    // Unlike greenlet we don't keep in the compiled code a chain of parent and
    // child threads of execution, that means we don't have another stack to
    // switch to and continue running, also we cannot raise an exception
    // SystemExit exception because there is no stack to unwind, so just
    // finalize the running interpreter.

#if PY_MAJOR_VERSION >= 3
    PyObject *pystdout, *pystderr;
    // The builtin print() is defined on Python/bltinmodule.c, this function
    // will call PyFile_WriteString in a file object.
    //
    // The file object can be either sys.stdout or sys.stderr, both of them are
    // set on Python/pylifecycle.c and by default they are buffered, from
    // Python's code:
    //
    //     stdin is always opened in buffered mode, first because it shouldn't
    //     make a difference in common use cases, second because TextIOWrapper
    //     depends on the presence of a read1() method which only exists on
    //     buffered streams.
    //
    // For this reason we need to flush the stdout and stderr of the vm before
    // printing our message, otherwise we are going to mess the user's printing
    // (and our tests will fail)
    pystdout = _PySys_GetObjectId(&PyId_stdout);
    pystderr = _PySys_GetObjectId(&PyId_stderr);
    _PyObject_CallMethodId(pystderr, &PyId_flush, "");
    _PyObject_CallMethodId(pystdout, &PyId_flush, "");
#endif

    // XXX: calling exit() is probably wrong for python embedded
    // let the user know why we are exiting
    // if (result == NULL) {
    if (PyErr_Occurred() != NULL) {
        // PyObject *exc, *val, *tb;
        // PyErr_Fetch(&exc, &val, &tb);
        // PyErr_NormalizeException(&exc, &val, &c_tb);
        PyErr_Print();

        // Calling Py_Finalize here will segfault
        fprintf(stderr, "mix: Fiber got to the end of stack\n");
        std::exit(2);
    } else {
        Py_Finalize();
        fprintf(stderr, "mix: Fiber got to the end of stack\n");
        std::exit(1);
    }

    // beyond this point the application will segfault
}

/**
 * Boost: [the context] can migrated between threads, but must not
 * reference thread-local storage.
 *
 * We need to check if it's okay with the interpreter for the context to
 * change thread
 **/
intptr_t python_jump(ctx::fcontext_t *origin, ctx::fcontext_t target, intptr_t arguments) {
    int recursion_depth;
    struct _frame *frame;
    PyThreadState *state;
    PyObject *exc_type, *exc_value, *exc_traceback;
    intptr_t result;

    // save interpreter state
    state = PyThreadState_Get();
    recursion_depth = state->recursion_depth;
    frame = state->frame;
    exc_type = state->exc_type;
    exc_value = state->exc_value;
    exc_traceback = state->exc_traceback;

    // call tracing? tracing needs to call back into interpreted code that
    // might change the running state

    // switch execution to the target fiber
    result = ctx::jump_fcontext(origin, target, arguments, false);
    // someone else returned

    // restore interpreter state
    state = PyThreadState_Get();
    state->recursion_depth = recursion_depth;
    state->frame = frame;
    state->exc_type = exc_type;
    state->exc_value = exc_value;
    state->exc_traceback = exc_traceback;

    return result;
}

py::object py_context_switch_args_kwds(Fiber* origin, Fiber *target, py::object args, py::object kwds) {
    PyObject *args_ptr=nullptr, *kwds_ptr=nullptr;

    args_ptr = args.ptr();
    kwds_ptr = kwds.ptr();

    if (! (PyTuple_Check(args_ptr) || PySequence_Check(args_ptr))) {
        PyErr_Format(PyExc_TypeError, "context_switch third argument must be a sequence");
        py::throw_error_already_set();
    }

    // XXX: how do I check for a mapping?
    // if (! (PyDict_Check(kwds_ptr) || PyMapping_Check(kwds_ptr))) {
    if (!PyDict_Check(kwds_ptr)) {
        PyErr_Format(PyExc_TypeError, "context_switch fourth argument must be a mapping");
        py::throw_error_already_set();
    }

    callback_t trampoline_arguments;
    arguments_t python_arguments;
    arguments_t* python_result;

    intptr_t arguments_ptr;
    intptr_t result_ptr;

    // The primed flag is used to say:
    //
    //      "We are resuming a fiber, so we are returning from an context_switch call."
    //
    // That means that all origins are primed and that if the target is not
    // primed we are first going to the trampoline.
    //
    // Force the origin to be primed, we are either leaving the main fiber or
    // using a new Fiber object from inside a running fiber, either way when
    // there is a switch back we will be returning from the context_switch() call.
    origin->primed = true;

    // if the target is primed we are returning an context_switch call, just pass the
    // python_arguments, otherwise we are priming a fiber and need to pass the
    // callback to the trampoline
    if (target->primed) {
        python_arguments = {args.ptr(), kwds.ptr()};
        arguments_ptr = (intptr_t)&python_arguments;
    } else {
        target->primed = true;
        trampoline_arguments = {target->callback.ptr(), args.ptr(), kwds.ptr()};
        arguments_ptr = (intptr_t)&trampoline_arguments;
    }

    // switch execution to the target fiber
    result_ptr = python_jump(
        &origin->execution_context,
        target->execution_context,
        arguments_ptr
    );
    // someone else returned

    python_result = (arguments_t*)result_ptr;
    return py::make_tuple(py::handle<>(python_result->args), py::handle<>(python_result->kwds));
}

py::object py_context_switch_args(Fiber* origin, Fiber *target, py::object args) {
    return py_context_switch_args_kwds(origin, target, args, py::dict());
}

py::object py_context_switch(Fiber* origin, Fiber *target) {
    return py_context_switch_args_kwds(origin, target, py::tuple(), py::dict());
}

BOOST_PYTHON_MODULE(fiber)
{
    using namespace boost::python;

    // always define the docstring, otherwise help(obj) will segfault
    def("context_switch", py_context_switch_args_kwds, "Store the current state on origin and change execution to target");
    def("context_switch", py_context_switch_args, "Store the current state on origin and change execution to target");
    def("context_switch", py_context_switch, "Store the current state on origin and change execution to target");

    class_<Fiber>("Fiber", "This class store a fiber state and stack", no_init)
        .def(init<object>())
        .def(init<object, std::size_t>())
        .def_readonly("size", &Fiber::size)
        .def_readonly("fls", &Fiber::fls);
}

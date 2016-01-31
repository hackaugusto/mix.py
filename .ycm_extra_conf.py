import os
import shutil
import subprocess

import ycm_core

SOURCE_EXTENSIONS = ['.cpp', '.cxx', '.cc', '.c', '.m', '.mm']
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DATABASE = os.path.join(ROOT_DIR, 'compile_commands.json')

# Create the compile_commands.json by intercepting the compiler executions with
# rizsotto/Bear
if not os.path.exists(ROOT_DATABASE):
    # distutils by default will use gcc to compile a c++ file, bear 2.1.3 will
    # treat gcc as a non c++ compiler and create the database using cc instead,
    # youcompleteme version 5ee7bd2, will assume that cc is a c compiler and
    # add the force the flag -x c, this will make the completer treat the file
    # as a c and as consequence all the c++ syntax will be invalid.
    #
    # the work around is to force a explicity c++ compiler so that bear
    # translate the call to c++ instead o cc and youcompleteme add -x c++
    # instead of -x c
    env = {'CC': 'clang++'}

    build = subprocess.Popen(['bear', 'python3', 'setup.py', 'build'], env=env)
    build.wait()
    shutil.rmtree(os.path.join(ROOT_DIR, 'build'))

database = ycm_core.CompilationDatabase(ROOT_DIR)


def MakeRelativePathsInFlagsAbsolute(flags, working_directory):
    make_next_absolute = False
    new_flags = []
    path_flags = ['-isystem', '-I', '-iquote', '--sysroot=']

    if not working_directory:
        return list(flags)

    for flag in flags:
        new_flag = flag

        if make_next_absolute:
            make_next_absolute = False
            if not flag.startswith('/'):
                new_flag = os.path.join(working_directory, flag)

        for path_flag in path_flags:
            if flag == path_flag:
                make_next_absolute = True
                break

            if flag.startswith(path_flag):
                path = flag[len(path_flag):]
                new_flag = path_flag + os.path.join(working_directory, path)
                break

        if new_flag:
            new_flags.append(new_flag)

    return new_flags


def IsHeaderFile(filename):
    extension = os.path.splitext(filename)[1]
    return extension in ['.h', '.hxx', '.hpp', '.hh']


def GetCompilationInfoForFile(database, filename):
    if IsHeaderFile(filename):
        basename = os.path.splitext(filename)[0]

        for extension in SOURCE_EXTENSIONS:
            replacement_file = basename + extension

            if os.path.exists(replacement_file):
                compilation_info = database.GetCompilationInfoForFile(replacement_file)

                if compilation_info.compiler_flags_:
                    return compilation_info
        return None

    return database.GetCompilationInfoForFile(filename)


def FlagsForFile(filename, **kwargs):
    compilation_info = GetCompilationInfoForFile(database, filename)

    flags = MakeRelativePathsInFlagsAbsolute(
        compilation_info.compiler_flags_,
        compilation_info.compiler_working_dir_,
    )
    print(flags)

    return {
        'flags': flags,
        'do_cache': True,
    }

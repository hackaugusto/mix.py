#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sts=4 sw=4 ts=4 et:
from __future__ import print_function

import os
import re
import subprocess


# these tests are really fragile, but are a good sanity check

test1_output = [
    b'first',
    b'mix: Fiber got to the end of stack',
]

test2_output = [
    b'first',
]

test3_output = [
    b'first',
    b'second',
]

test4_output = [
    b'first',
    b'second',
]

test5_output = [
    b'first',
    b'jump',
    b'second',
    b'jump',
    b'third',
]

testargs1_output = [
    b'() {}',
]

testargs2_output = [
    b'(1,) {}',
]

testargs3_output = [
    b'(1, 2, 3) {}',
]

testargs4_output = [
    b'() {}',
]

testargs5_output = [
    b"() {'a': 1}",
]

testargs6_output = [
    b"(1, 2) OrderedDict([('a', 1), ('b', 2)])",
]

testargs7_output = [
    b"Traceback (most recent call last):",
    re.compile('^File "[^"]+", line \d+, in <module>$'),
    re.compile('^mix.context_switch[(]'),
    b'TypeError: context_switch third argument must be a sequence',
]

testargs9_output = [
    b"Traceback (most recent call last):",
    re.compile('^File "[^"]+", line \d+, in <module>$'),
    re.compile('^mix.context_switch[(]'),
    b'TypeError: context_switch fourth argument must be a mapping',
]

testreturn1_output = [
    b'() {}',
]

testreturn2_output = [
    b'(1,) {}',
]

testreturn3_output = [
    b'(1, 2, 3) {}',
]

testreturn4_output = [
    b'() {}',
]

testreturn5_output = [
    b"() {'a': 1}",
]

testreturn6_output = [
    b"(1, 2) OrderedDict([('a', 1), ('b', 2)])",
]

RESULTS = [
    ('test1.py', test1_output, 1),
    ('test2.py', test2_output, 0),
    ('test3.py', test3_output, 0),
    ('test4.py', test4_output, 1),
    ('test5.py', test5_output, 0),
    ('test6.py', [], 0),

    ('test_args1.py', testargs1_output, 0),
    ('test_args2.py', testargs2_output, 0),
    ('test_args3.py', testargs3_output, 0),
    ('test_args4.py', testargs4_output, 0),
    ('test_args5.py', testargs5_output, 0),
    ('test_args6.py', testargs6_output, 0),
    ('test_args7.py', testargs7_output, 1),
    ('test_args8.py', [], 0),
    ('test_args9.py', testargs9_output, 1),

    ('test_return1.py', testreturn1_output, 0),
    ('test_return2.py', testreturn2_output, 0),
    ('test_return3.py', testreturn3_output, 0),
    ('test_return4.py', testreturn4_output, 0),
    ('test_return5.py', testreturn5_output, 0),
    ('test_return6.py', testreturn6_output, 0),
]


def decode(data):
    if isinstance(data, bytes):
        return data.decode('utf8')
    return data


def match_output(output, expected):
    for output_line, excpected_line in zip(output.split(b'\n'), expected):
        output_line = decode(output_line).strip()

        if hasattr(excpected_line, 'match'):
            if not excpected_line.match(output_line):
                return (output_line, excpected_line)

        else:
            # we can't decode and strip a regex
            excpected_line = decode(excpected_line).strip()

            if output_line != excpected_line:
                return (output_line, excpected_line)
    return False


RETURNCODE_SIGNAL = {
    1: 'SIGHUP',        # Exit    Hangup
    2: 'SIGINT',        # Exit    Interrupt
    3: 'SIGQUIT',       # Core    Quit
    4: 'SIGILL',        # Core    Illegal Instruction
    5: 'SIGTRAP',       # Core    Trace/Breakpoint Trap
    6: 'SIGABRT',       # Core    Abort
    7: 'SIGEMT',        # Core    Emulation Trap
    8: 'SIGFPE',        # Core    Arithmetic Exception
    9: 'SIGKILL',       # Exit    Killed
    10: 'SIGBUS',       # Core    Bus Error
    11: 'SIGSEGV',      # Core    Segmentation Fault
    12: 'SIGSYS',       # Core    Bad System Call
    13: 'SIGPIPE',      # Exit    Broken Pipe
    14: 'SIGALRM',      # Exit    Alarm Clock
    15: 'SIGTERM',      # Exit    Terminated
    16: 'SIGUSR1',      # Exit    User Signal 1
    17: 'SIGUSR2',      # Exit    User Signal 2
    18: 'SIGCHLD',      # Ignore  Child Status
    19: 'SIGPWR',       # Ignore  Power Fail/Restart
    20: 'SIGWINCH',     # Ignore  Window Size Change
    21: 'SIGURG',       # Ignore  Urgent Socket Condition
    22: 'SIGPOLL',      # Ignore  Socket I/O Possible
    23: 'SIGSTOP',      # Stop    Stopped (signal)
    24: 'SIGTSTP',      # Stop    Stopped (user)
    25: 'SIGCONT',      # Ignore  Continued
    26: 'SIGTTIN',      # Stop    Stopped (tty input)
    27: 'SIGTTOU',      # Stop    Stopped (tty output)
    28: 'SIGVTALRM',    # Exit    Virtual Timer Expired
    29: 'SIGPROF',      # Exit    Profiling Timer Expired
    30: 'SIGXCPU',      # Core    CPU time limit exceeded
    31: 'SIGXFSZ',      # Core    File size limit exceeded
    32: 'SIGWAITING',   # Ignore  All LWPs blocked
    33: 'SIGLWP',       # Ignore  Virtual Interprocessor Interrupt for Threads Library
    34: 'SIGAIO',       # Ignore  Asynchronous I/O
}


if __name__ == '__main__':
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    for test_script, excpected_output, expected_returncode in RESULTS:
        try:
            output = subprocess.check_output(os.path.join(DIRECTORY, test_script), stderr=subprocess.STDOUT, shell=True, close_fds=True)
            returncode = 0
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode

        returncode_msg = 'test {} returned wrong code, got: {}, excpected: {}.\nfull output:\n{}'.format(
            test_script,
            RETURNCODE_SIGNAL.get(abs(returncode), returncode),
            expected_returncode,
            output,
        )

        assert returncode == expected_returncode, returncode_msg

        error = match_output(output, excpected_output)
        assert not error, 'test {} failed with wrong output: given "{}", excpected "{}".\nfull output:\n{}'.format(
            test_script,
            error[0],
            error[1],
            output,
        )

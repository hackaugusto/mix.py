#!/usr/bin/sh

tox
source ./.tox/py27/bin/activate

/usr/bin/expect -c '''
spawn gdb -nh

expect -exact "(gdb)"
send "file python\n"

expect -exact "(gdb)"
send "break mix.cpp:111\n"

expect -exact "Make breakpoint pending on future shared library load?"
send "y\n"

expect -exact "(gdb)"
send "run\n"

expect -exact ">>>"

send -- "
import mix

def noop():
    pass

f1 = mix.Fiber(noop)
"

interact

'''

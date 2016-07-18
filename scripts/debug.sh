#!/usr/bin/bash

error() {
    printf "$(tput setaf 1)$@$(tput sgr0)\n" >&2
    exit
}

(
    cd ./mix
    make clean
    make
)
pip install -e .

[ -z "${PYTHON}" ] && [ ! -z "${PYENV_ROOT}" ] && {
    PYTHON=$(pyenv which python)
}

: ${PYTHON:=python}

[ -n "${PYTHON_SOURCE}" ] && {
    ADD_SOURCE="
expect -exact \"(gdb)\"
send \"dir ${PYTHON_SOURCE}\n\"
"
}

# if the user didn't ask to run as test just initialize a session
[ $# -eq 0 ] && {
    RUN_CMD='
expect -exact "(gdb)"
send "run\n"

expect -exact ">>>"

send -- "
import mix

def noop():
    pass

f1 = mix.Fiber(noop)
"
'
}

# expect -exact "(gdb)"
# send "break fiber.cpp:111\n"

# else check that the test file exists and run a session with it
[ $# -ne 0 -a ! -e "${1}" ] && error "file ${1} does not exists"
[ $# -ne 0 -a ! -f "${1}" ] && error "${1} is not a file"
[ $# -ne 0 -a ! -x "${1}" ] && error "${1} is not an executable file"
[ $# -ne 0 ] && {
    RUN_CMD="
expect -exact \"(gdb)\"
send \"run ${1}\"
"
}

read -r -d '' SCRIPT <<EOS
spawn gdb

expect -exact "(gdb)"
send "file ${PYTHON}\n"

${ADD_SOURCE}

expect -exact "(gdb)"
send "dir mix\n"

$RUN_CMD

interact

EOS

/usr/bin/expect -c "${SCRIPT}";
exit $?;

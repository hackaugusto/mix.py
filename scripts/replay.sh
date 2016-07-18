#!/usr/bin/bash

error() {
    printf "$(tput setaf 1)$@$(tput sgr0)\n" >&2
    exit
}

[ $# -ne 1 ] && error "${0} <testname>"
[ ! -e "${1}" ] && error "file ${1} does not exists"
[ ! -f "${1}" ] && error "${1} is not a file"
[ ! -x "${1}" ] && error "${1} is not an executable file"

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

rr record $PYTHON $1

[ -n "${PYTHON_SOURCE}" ] && {
    ADD_SOURCE="
expect -exact \"(rr)\"
send \"dir ${PYTHON_SOURCE}\n\"
"
}

read -r -d '' SCRIPT <<EOS
spawn rr replay

expect -exact "(rr)"
send "file ${PYTHON}\n"

${ADD_SOURCE}

expect -exact "(rr)"
send "dir mix\n"

interact

EOS

/usr/bin/expect -c "${SCRIPT}";
exit $?;

#!/bin/bash
set -e
function finish {
  cd $owd
}

# FIXME put some of the below in a common routine
owd=$(pwd)
trap finish EXIT

cd $(dirname ${BASH_SOURCE[0]})

if ! source ./pyenv-3.1-3.2-versions ; then
    exit $?
fi
cd ..
[[ -f test/.python-version ]] && rm -v test/.python-version
(cd ../python-xdis/admin-tools && source ./setup-python-3.1.sh)
git checkout python-3.1-to-3.2

for version in $PYVERSIONS; do
    echo --- $version ---
    if ! pyenv local $version ; then
	exit $?
    fi
    make clean && pip install -e .
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done

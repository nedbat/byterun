#!/bin/bash
# Simple script to create bytecode files from Python source
if [[ $# == 0 ]]; then
    print 2>&1 "Need to pass a python file to compile"
fi
mydir=$(dirname ${BASH_SOURCE[0]})

(cd ../../python-xdis && . ./admin-tools/setup-master.sh)
# Note: Python < 2.7 is added at the end and 2.6.9 is used as a sentinal in the version test below
PYENV_VERSIONS=${PYENV_VERSIONS:-"3.6.14 3.7.11 3.8.11 3.9.7 3.3.7 3.4.10 3.2.6 3.5.9 2.7.18 2.6.9 2.5.6 2.4.6"}
for version in $PYENV_VERSIONS; do
    # Note: below we use
    if [[ $version == 2.6.9 ]]; then
        (cd ../../python-xdis && . ./admin-tools/setup-python-2.4.sh)
    fi
    for file in $*; do
        pyenv local $version
	    python ${mydir}/compile-file.py "$file"
    done
    short=$(basename $file .py)
    git add -f ${mydir}/bytecode-*/${short}*
    rm -v .pyenv_version *~ 2>/dev/null || /bin/true
done
rm -v .python-version 2>/dev/null || /bin/true
(cd ../../python-xdis && . ./admin-tools/setup-master.sh)

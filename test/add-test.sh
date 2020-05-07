#!/bin/bash
# Simple script to create bytecode files from Python source
if [[ $# == 0 ]]; then
    print 2>&1 "Need to pass a python file to compile"
fi
mydir=$(dirname ${BASH_SOURCE[0]})

PYENV_VERSIONS=${PYENV_VERSIONS:-"3.6.10 3.7.7 3.3.7 3.4.10 2.7.18 2.6.9 2.5.6 3.2.6 3.5.9"}
for file in $*; do
    for version in $PYENV_VERSIONS; do
	pyenv local $version
	python ${mydir}/compile-file.py "$file"
    done
    rm -v .pyenv_version *~ || /bin/true
    short=$(basename $file .py)
    git add -f ${mydir}./bytecode-*/${short}*
done
rm .python-version

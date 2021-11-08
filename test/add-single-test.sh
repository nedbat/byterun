#!/bin/bash
# Simple script to create a single bytecode files from Python source
if [[ $# == 0 ]]; then
    print 2>&1 "Need to pass a python file to compile"
fi
mydir=$(dirname ${BASH_SOURCE[0]})

for file in $*; do
    pyenv local $version
    python ${mydir}/compile-file.py "$file"
    short=$(basename $file .py)
    git add -f ${mydir}/bytecode-*/${short}*
done

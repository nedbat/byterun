#!/bin/bash
# Simple script to create bytecode files from Python source
if [[ $# == 0 ]]; then
    print 2>&1 "Need to pass a python file to compile"
fi
mydir=$(dirname ${BASH_SOURCE[0]})

(cd ../../python-xdis && . ./admin-tools/setup-master.sh)
PYENV_VERSIONS=${PYENV_VERSIONS:-"pypy3.5-6.0.0 pypy3.7-7.3.5 pypy3.6-7.3.1"}
for version in $PYENV_VERSIONS; do
    # Note: below we use
    for pyc in bytecode-3.6/*.pyc; do
		file=$(strings $pyc | grep examples/ | sed -e 's:.*examples/:examples/:')
        pyenv local $version
	    python ${mydir}/compile-file.py "$file"
    done
    short=$(basename $file .py)
    git add -f ${mydir}/bytecode-*/${short}*
    rm -v .pyenv_version *~ 2>/dev/null || /bin/true
done
rm -v .python-version 2>/dev/null || /bin/true

#!/bin/bash
# Test a single Python version, e.g. 3.7.16
# using only that bytecode for that version
# e.g. byteocde-3.7.
set -e

PYTHON=${PYTHON:-python}
PYTHON_VERSION=`python -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2`
VERBOSE=${VERBOSE:-0}
XPYTHON_OPTS=${XPYTHON_OPTS:-""}

echo Testing Python $PYTHON_VERSION

bytecode_dir="bytecode-${PYTHON_VERSION}"
for file in ${bytecode_dir}/*.pyc ; do
    (( $VERBOSE )) && echo $file
    if ! xpython ${XPYTHON_OPTS} $file ; then
	echo "$file broken"
	break
    fi
done

#!/bin/bash
# Simple script to run xpython all bytecode
if (( $# > 0 )); then
    # FIXME
    print "Arg not handled yet"
    exit 1
fi
mydir=$(dirname ${BASH_SOURCE[0]})
set -e

source ../admin-tools/pyenv-3.1-3.2-versions

(cd ../../python-xdis && . ./admin-tools/setup-master.sh)
# Note: Python < 2.7 is added at the end and 2.6.9 is used as a sentinal in the version test below
for version in $PYVERSIONS; do
    pyenv local $version
    echo "Using Python $version"
    first_two=$(echo $version | cut -d'.' -f 1-2)
    for file in bytecode-${first_two}/*.pyc; do
	echo ======= $file ========
	xpython "$file"
	echo ------- $file --------
    done
done
rm .python-version

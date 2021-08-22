#!/bin/bash
# Simple script to run xpython all bytecode
if (( $# > 0 )); then
    # FIXME
    print "Arg not handled yet"
    exit 1
fi
mydir=$(dirname ${BASH_SOURCE[0]})
set -e

(cd ../../python-xdis && . ./admin-tools/setup-master.sh)
# Note: Python < 2.7 is added at the end and 2.6.9 is used as a sentinal in the version test below
PYENV_VERSIONS=${PYENV_VERSIONS:-"3.6.13 3.7.10 3.8.8 3.9.2 3.3.7 3.4.10 3.2.6 3.5.9 2.7.18 2.6.9 2.5.6 2.4.6"}
for version in $PYENV_VERSIONS; do
    pyenv local $version
    echo "Using Python $version"
    # Note: below we use
    if [[ $version == 2.6.9 ]]; then
	break
    fi
    first_two=$(echo $version | cut -d'.' -f 1-2)
    for file in bytecode-${first_two}/*.pyc; do
	echo ======= $file ========
	xpython "$file"
	echo ------- $file --------
    done
done
rm .python-version

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
pyenv local 2.7.18
OLDPYENV_VERSIONS=${OLDPYENV_VERSIONS:-"2.6.9 2.5.6 2.4.6"}
for version in $OLDPYENV_VERSIONS; do
    echo "Testing Python $version"
    # Note: below we use
    first_two=$(echo $version | cut -d'.' -f 1-2)
    for file in bytecode-${first_two}/*.pyc; do
	echo ======= $file ========
	xpython "$file"
	echo ------- $file --------
    done
done
rm .python-version

#!/bin/bash
PYTHON_VERSION=3.2.6
pyenv local $PYTHON_VERSION

owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi
mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
cd $fulldir/..
(cd ../python-xdis && . ./admin-tools/setup-python-3.0 && git pull)
git checkout python-3.1-to-3.2
cd $owd
rm -v */.python-version >/dev/null 2>&1 || true

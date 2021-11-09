#!/bin/bash
PYTHON_VERSION=3.3.7
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
(cd ../python-xdis && git checkout python-3.3 && pyenv local $PYTHON_VERSION) && git pull && \
    git checkout python-3.3 && pyenv local $PYTHON_VERSION && git pull
(cd ../python-uncompyle6 && ./admin-tools/setup-python-3.3.sh)
cd $owd
rm -v */.python-version >/dev/null 2>&1 || true

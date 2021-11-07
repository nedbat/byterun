#!/bin/bash
PYTHON_VERSION=3.5.10
pyenv local $PYTHON_VERSION

owd=$(pwd)
bs=${BASH_SOURCE[0]}

mydir=$(dirname $bs)
fulldir=$(readlink -f $mydir)
cd $fulldir/..
(cd ../python-xdis && ./admin-tools/setup-python-3.3.sh)
cd $owd
rm -v */.python-version || true

git checkout python-3.5  && git pull && pyenv local $PYTHON_VERSION

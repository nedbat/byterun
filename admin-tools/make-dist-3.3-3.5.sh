#!/bin/bash
PACKAGE=x-python

# FIXME put some of the below in a common routine
function finish {
  cd $owd
}

cd $(dirname ${BASH_SOURCE[0]})
owd=$(pwd)
trap finish EXIT

if ! source ./pyenv-3.3-3.5-versions ; then
    exit $?
fi
if ! source ./setup-python-3.3.sh ; then
    exit $?
fi

cd ..
source xpython/version.py
echo $__version__

for pyversion in $PYVERSIONS; do
    echo --- $pyversion ---
    if ! pyenv local $pyversion ; then
  	    exit $?
    fi
    # pip bdist_egg create too-general wheels. So
    # we narrow that by moving the generated wheel.

    # Pick out first two number of version, e.g. 3.5.1 -> 35
    first_two=$(echo $pyversion | cut -d'.' -f 1-2 | sed -e 's/\.//')
    rm -fr build
    python setup.py bdist_egg bdist_wheel
    if [[ $first_two =~ py* ]]; then
	if [[ $first_two =~ pypy* ]]; then
	    # For PyPy, remove the what is after the dash, e.g. pypy37-none-any.whl instead of pypy37-7-none-any.whl
	    first_two=${first_two%-*}
	fi
	mv -v dist/${PACKAGE}-$__version__-{py3,$first_two}-none-any.whl
    else
	mv -v dist/${PACKAGE}-$__version__-{py3,py$first_two}-none-any.whl
    fi
    echo === $pyversion ===
done

python ./setup.py sdist

tarball=dist/${PACKAGE}-${__version__}.tar.gz
if [[ -f $tarball ]]; then
    mv -v $tarball dist/${PACKAGE}_33-${__version__}.tar.gz
fi

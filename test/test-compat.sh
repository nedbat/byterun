#!/bin/bash
set -e

VERBOSE=${VERBOSE:-0}

source ../admin-tools/pyenv-newest-versions
PYVERSIONS="pypy3.7-7.3.5 pypy3.6-7.3.1 $PYVERSIONS"
# FIXME: we need to fix up pypy bytecode. Skip for now
for PYENV_VERSION in $PYVERSIONS; do
	echo -----------------------------------------
	echo Testing Python version $PYENV_VERSION ...
	pyenv local $PYENV_VERSION

	for bytecode_dir in bytecode-* ; do
		echo testing $bytecode_dir ...
		for file in ${bytecode_dir}/*.pyc ; do
			(( $VERBOSE )) && echo $file
			if ! xpython $file >/dev/null ; then
				echo "$file broken"
				break
			fi
		done
	done
	echo -----------------------------------------
done

# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8
SHELL   ?= bash

PHONY=all check check-compat check-full clean unittest dist distclean lint flake8 test rmChangeLog clean_pyc

#: Default target - same as "check"
all: check

# Run all tests, exluding those that need pyenv
check:
	test -f test/.python-version && rm -v test/.python-version || true
	cd test && pyenv local && SKIP_COMPAT=1 nosetests --stop

#: Check across all Python versions
check-full:
	SKIP_COMPAT=1 bash ./admin-tools/check-versions.sh

# There is a bug somewhere that causes check-compat not to run
# when run with the other tests.
#: Check across all Python versions
check-compat:
	pyenv local 2.7.18 && nosetests --stop test/test_compat.py

#: Clean up temporary files and .pyc files
clean: clean_pyc
	$(PYTHON) ./setup.py $@
	find . -name __pycache__ -exec rm -fr {} \; || true

#: Create source (tarball) and wheel distribution
dist: clean
	$(PYTHON) ./setup.py sdist bdist_wheel

#: Remove .pyc files
clean_pyc:
	( cd xpython && $(RM) -f *.pyc */*.pyc )
	( cd tests && $(RM) -f *.pyc */*.pyc )

#: Create source tarball
sdist:
	$(PYTHON) ./setup.py sdist

#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint: flake8

#: Check StructuredText long description formatting
check-rst:
	$(PYTHON) setup.py --long-description | rst2html.py > x-python.html

#: Lint program
flake8:
	$(LINT) xpython

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg


#: Create binary wheel distribution
bdist_wheel:
	$(PYTHON) ./setup.py bdist_wheel

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.pyc

#: Remove ALL derived files
distclean: clean
	-rm -fvr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

#: Install package locally
verbose-install:
	$(PYTHON) ./setup.py install

#: Install package locally without the verbiage
install:
	$(PYTHON) ./setup.py install >/dev/null

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)

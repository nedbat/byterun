# Compatibility for us old-timers.

.PHONY: all check check-nosetests check-version-bytecode

PYTHON ?= python
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8
SHELL   ?= bash
SKIP_COMPAT ?= 1
o       ?= ""

#: Default target - same as "check"
all: check check-version-bytecode

check: check-nosetests check-version-bytecode

#: Run all tests, excluding those that need pyenv
check-nosetests:
	$(PYTHON) -V && SKIP_COMPAT=$(SKIP_COMPAT) nosetests --stop $(o)

#: Run all tests, excluding those that need pyenv
check-version-bytecode:
	$(BASH) ./test-single-version.sh

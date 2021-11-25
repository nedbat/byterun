# Compatibility for us old-timers.

.PHONY: all check

PYTHON ?= python
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8
SHELL   ?= bash
SKIP_COMPAT ?= 1

#: Default target - same as "check"
all: check

# Run all tests, excluding those that need pyenv
check:
	$(PYTHON) -V && SKIP_COMPAT=$(SKIP_COMPAT) nosetests --stop

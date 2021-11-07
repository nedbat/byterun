# This file is needs to be multi-lingual in both Python and POSIX
# shell which "exec()" or "source" it respectively.

# This file should define a variable __version__ which we use as the
# debugger version number.

# fmt: off
__version__="1.4.0"  # noqa
# fmt: on

# FIXME: move below into python_version and keep this multilingual.

# The below has extra commas for POSIX shell's taste, but that's okay
SUPPORTED_PYTHON = (
    (2, 7),
    (3, 3),
    (3, 2),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (3, 9),
)

# PYPY 3.7 and 3.8 aren't ready yet
# SUPPORTED_PYPY = ((2, 7), (3, 2), (3, 5), (3, 6), (3, 7), (3, 8))  # noqa
SUPPORTED_PYPY = ((2, 7), (3, 2), (3, 5), (3, 6))  # noqa

SUPPORTED_BYTECODE = (
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (3, 3),
    (3, 2),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (3, 9),
)

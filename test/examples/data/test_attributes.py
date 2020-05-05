# Tests attribute access which in particular means

# Tests opcodes:
#   LOAD_NAME, STORE_NAME LOAD_ATTR and DELETE_ATTR

# Since this program doesn't have any subroutine calls (and subroutine
# parameter conventions in Python are complicated and change from
# version to version), this is a good program to try when expanding
# the interpreter such as for a new Python version.

"""This program is self-checking!"""

l = lambda: 1   # Just to have an object...
l.foo = 17
assert hasattr(l, "foo")
assert l.foo == 17
del l.foo
assert hasattr(l, "foo") == False

# This program stresses WITH_FINALLY and in 3.5+
# WITH_CLEANUP_FINISH.

# Compare with test_suppressed_raise_context_manager.py
"""This program is self-checking!"""


class NullContext(object):
    def __enter__(self):
        l.append("i")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert exc_type is ValueError, "Expected ValueError: %r" % exc_type
        l.append("o")
        return False


l = []
try:
    with NullContext():
        l.append("w")
        raise ValueError("Boo!")
    l.append("e")
except ValueError:
    # Raise should propagate to here
    l.append("-propagated-")
l.append("r")
s = "".join(l)

expect = "iwo-propagated-r"
assert s == expect, "'%s' vs '%s'" % (s, expect)

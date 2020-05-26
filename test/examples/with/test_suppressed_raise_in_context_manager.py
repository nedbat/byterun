# This program stresses WITH_FINALLY and in 3.5+
# WITH_CLEANUP_FINISH
# Compare with test_raise_in_context_manager.py
"""This program is self-checking!"""

class SuppressingContext(object):
    def __enter__(self):
        l.append("i")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert exc_type is ValueError, "Expected ValueError: %r" % exc_type
        l.append("o")
        return True


l = []
try:
    # Check that "with SuppressingContext()" suppresses the below raise ValueError()
    with SuppressingContext():
        l.append("w")
        raise ValueError("Boo!")
    l.append("-suppressed-")
except ValueError:
    # Raise does should propagate to here
    l.append("-propagated-")
l.append("r")
s = "".join(l)
assert s == "iwo-suppressed-r", "'%s' vs '%s'" % (s, "iwo-suppressed-r")

# This program stresses WITH_FINALLY and in 3.5+
# WITH_CLEANUP_FINISH.

# Compare with test_suppressed_raise_context_manager.py
"""This program is self-checking!"""


class NullContext(object):
    def __enter__(self):
        l.append("i")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        l.append("o")
        return False


l = []
try:
    with NullContext():
        l.append("w")
        raise ValueError("oops")
        l.append("z")
    l.append("e")
except ValueError as e:
    assert str(e) == "oops"
    l.append("x")
l.append("r")
s = "".join(l)

expect = "iwoxr"
assert s == expect, "'%s' vs '%s'" % (s, expect)

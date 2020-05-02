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
    l.append("x")
l.append("r")
s = "".join(l)
print("Look: %r" % s)
assert s == "iwoxr"

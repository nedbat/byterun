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
print("Look: %r" % s)
assert s == "iwoxr", "What!?"

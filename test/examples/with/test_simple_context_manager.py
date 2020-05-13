class NullContext(object):
    def __enter__(self):
        l.append('i')
        # __enter__ usually returns self, but doesn't have to.
        return 17

    def __exit__(self, exc_type, exc_val, exc_tb):
        l.append('o')
        return False

l = []
for i in range(3):
    with NullContext() as val:
        assert val == 17
        l.append('w')
    l.append('e')
l.append('r')
s = ''.join(l)
assert s == "iwoeiwoeiwoer"

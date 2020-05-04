class NullContext(object):
    def __enter__(self):
        l.append('i')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        l.append('o')
        return False

l = []
for i in range(3):
    with NullContext():
        l.append('w')
        if i % 2:
           break
        l.append('z')
    l.append('e')

l.append('r')
s = ''.join(l)
print("Look: %r" % s)
assert s == "iwzoeiwor"

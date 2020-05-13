# This test is good for checking
# WITH_CLEANUP (< 3.5) or WITH_CLEANUP_START/WITH_CLEANUP_FINISH
# In particular there is a custom __exit__ handler

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
           continue
        l.append('z')
    l.append('e')

l.append('r')
s = ''.join(l)
assert s == "iwzoeiwoiwzoer"

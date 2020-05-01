# In addition to testing attributes, this
# is a simple class test.

class Thing(object):
    z = 17
    def __init__(self):
        self.x = 23
t = Thing()

print(Thing.z)
assert Thing.z == 17
print(t.z)
print(t.x)

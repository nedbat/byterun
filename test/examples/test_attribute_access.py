class Thing(object):
    z = 17
    def __init__(self):
        self.x = 23
t = Thing()
print(Thing.z)
print(t.z)
print(t.x)

# Adapted from byterun test_basic.py test
"""This program is self-checking!"""

class Thing(object):
    def __init__(self, x):
        self.x = x
    def meth(self, y):
        return self.x * y
thing1 = Thing(2)
try:
    Thing.meth(14)
except TypeError:
    pass
else:
    assert True, "Should have gotten: TypeError: meth() missing 1 required positional argument: 'y'"

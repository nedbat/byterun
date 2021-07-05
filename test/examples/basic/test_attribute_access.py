# In addition to testing attributes, this
# is a simple class test.
# Adapted from the a test in byterun's test_basic.py.

"""This program is self-checking!"""


class Thing(object):
    z = 17

    def __init__(self):
        self.x = 23


t = Thing()

assert Thing.z == 17
assert t.z == 17
assert t.x == 23

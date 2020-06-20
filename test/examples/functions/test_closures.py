"""This program is self-checking!"""

# Variables in inner nested functions accessing values from the
# encompasing functions.
# Notice that free_var and cell_var indices refer to different
# variables as we nest.
def f2(c):
    d = 2*c
    def f3(e):
        f = 2*e
        def f4(g):
            h = 2*g
            expect = (4, 8, 5, 10, 6, 12)
            assert (c,d,e,f,g, h) == expect, "got: %s, expect: %s" % ((c,d,e,f,g, h), expect)
            return c+d+e+f+g+h
        return f4
    return f3

expect = 4+8+5+10+6+12
answer = f2(4)(5)(6)
assert answer == expect, "f1(3)(4)(5)(6) is %d; should be %d." % (answer, expect)

# From test_audiop.py
# This is an example where we to create a function with a non-zero
# closure tuple of cells. In some versions we'll need to convert
# our Cell type into a native cell type if we want to create a native
# function.

import sys
if sys.version_info[0:1] >= (2, 7):
    # Use eval to be compatible with Pythons before 2.7
    null_byte = eval("b''")
    def pack(width, data):
        return b''null_byte.join(v.to_bytes(
            width, "little",
            signed=True)
                        for v in data)

    packs = {
        w:
        (lambda data, width=w: pack(width, data))
        for w in
        (1, 2, 3, 4)
        }
    assert packs[3](data=[0, -1, 0x123456]) == b'\x00\x00\x00\xff\xff\xffV4\x12'

def make_adder(x):
    def add(y):
        return x+y
    return add
a = make_adder(10)
assert a(7) == 17

# The below were adaped from byterun test_functions tests.

def make_adder_store_deref(x):
    z = x+1
    def add(y):
        return x+y+z
    return add
a = make_adder_store_deref(10)
assert a(7) == 28

# test closure in a loop
def make_fns(x):
    fns = []
    for i in range(x):
        fns.append(lambda i=i: i)
    return fns
fns = make_fns(3)
assert (fns[0](), fns[1](), fns[2]()) == (0, 1, 2)

# test closure with defaults parameter values
def make_adder_with_defaults(x, y=13, z=43):
    def add(q, r=11):
        return x+y+z+q+r
    return add
a = make_adder_with_defaults(10, 17)
assert a(7) == 88

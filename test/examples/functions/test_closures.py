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
    def pack(width, data):
        return b''.join(v.to_bytes(
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

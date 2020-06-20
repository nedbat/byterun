# Converted from the corresponding byterun test
"""This program is self-checking!"""

from _functools import partial

def f(a,b):
    return a-b

f7 = partial(f, 7)
four = f7(3)
assert four == 4

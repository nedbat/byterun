# Subscripting tests
# This originally from byterun was adapted from test_base.py
"""This program is self-checking!"""

l = list(range(10))
assert (0, 3, 9) == (l[0], l[3], l[9])

l = list(range(10))
l[5] = 17
assert l == [0, 1, 2, 3, 4, 17, 6, 7, 8, 9]

l = list(range(10))
del l[5]
assert l == [0, 1, 2, 3, 4, 6, 7, 8, 9]

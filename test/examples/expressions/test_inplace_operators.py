# Inplace operator tests
"""This program is self-checking!"""

x, y = 2, 3
x **= y
assert x == 8 and y == 3
x *= y
assert x == 24 and y == 3
x //= y
assert x == 8 and y == 3
x %= y
assert x == 2 and y == 3
x += y
assert x == 5 and y == 3
x -= y
assert x == 2 and y == 3
x <<= y
assert x == 16 and y == 3
x >>= y
assert x == 2 and y == 3

x = 0x8F
x &= 0xA5
assert x == 0x85
x |= 0x10
assert x == 0x95
x ^= 0x33
assert x == 0xA6

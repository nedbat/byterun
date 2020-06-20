# Converted from the corresponding byterun test
"""This program is self-checking!"""

def fact(n):
    if n <= 1:
        return 1
    else:
        return n * fact(n-1)
f6 = fact(6)
assert f6 == 720

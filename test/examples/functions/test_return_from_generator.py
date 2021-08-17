# Adapted from byterun test_functions.py test
# Tests returning from a generator
"""This program is self-checking!"""


def gen():
    yield 1
    return 2


x = gen()
while True:
    try:
        assert next(x) == 1
    except StopIteration as e:
        assert e.value == 2
        break

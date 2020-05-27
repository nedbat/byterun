# Tests Python 3.3+ `yield from` statement and
# YEILD_FROM opcode.
"""This program is self-checking!"""
def main():
    i = 0
    for x in outer():
        i += 1
        assert x == i, "%d vs %d" % (x, i)

def outer():
    yield from (1, 2, 3, 4)

main()

# Tests deletions of various kinds
"""This program is self-checking!"""

# Ensures opcodes DELETE_SUBSCR and DELETE_GLOBAL are covered
a = (1, 2, 3)
assert "a" in locals()

# DELETE_NAME
del a
assert "a" not in locals()

# DELETE_SUBSCR
b = [4, 5, 6]
del b[1]
assert b == [4, 6]

del b[:]
assert b == []

# delete ::= expr expr DELETE_SLICE+1
l = [None] * 10
del l[-2:]
assert l == [None, None, None, None, None, None, None, None]

c = [0, 1, 2, 3, 4]
del c[:1]
del c[2:3]

d = [0, 1, 2, 3, 4, 5, 6]
del d[1:3:2]

e = ("a", "b")


def foo():
    # covers DELETE_GLOBAL
    global e
    del e


z = {}


def a():
    b = 1
    global z
    del z

    def b(y):
        global z
        # covers DELETE_FAST
        del y
        # LOAD_DEREF
        return z


a()

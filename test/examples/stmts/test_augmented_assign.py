# 01_augmented_assign.py modified from
#
# augmentedAssign.py -- source test pattern for augmented assigns
#
# This source is was adapted from the decompyle test suite.

# RUNNABLE!
"""This program is self-checking!"""

a = 1
b = 2

a += b
assert a == 3

a -= b;
assert a == 1

a *= b
assert a == 2

a |= a
assert a == 2

a &= a
assert a == 2

a **= a
assert a == 4

a ^= a
assert a == 0

a += 7*3
assert a == 21

l = [1,2,3]
l[1] *= 3

assert l == [1, 6, 3]

# Python 2.x
# aug_assign1 ::= expr expr inplace_op ROT_TWO   STORE_SLICE+0
l[:] += [9]

assert l == [1, 6, 3, 9]

# Python 2.x
#  aug_assign1 ::= expr expr inplace_op ROT_THREE STORE_SLICE+2
l[:2] += [8]
assert l == [1, 6, 8, 3, 9]

# Python 2.x
# augassign1 ::= expr expr inplace_op ROT_THREE STORE_SLICE+1
l[1:] += [0]

assert l == [1, 6, 8, 3, 9, 0]

# Python 2.x
# augassign1 ::= expr expr inplace_op ROT_FOUR STORE_SLICE+3
l[1:4] += [2]; # print l
assert l == [1, 6, 8, 3, 2, 9, 0]

l += [42, 43]
assert l == [1, 6, 8, 3, 2, 9, 0, 42, 43]

l = []

l = [
    [[0, 0], [0, 1]],
    [[[1, 0, 0], [1, 0, 1], [1, 0, 2]]]
    ]

# a.value = 1
# a.value += 1;
# a.b.val = 1
# a.b.val += 1;

l[0][1][1] = 7
assert l == [[[0, 0], [0, 7]], [[[1, 0, 0], [1, 0, 1], [1, 0, 2]]]]

l[0] *= 2
assert l == [[[0, 0], [0, 7], [0, 0], [0, 7]], [[[1, 0, 0], [1, 0, 1], [1, 0, 2]]]]

# i = j = k = 0
# def f():
#     global i
#     i += 1
#     return i

# assert l[f()][j][k] == [1, 0, 0]

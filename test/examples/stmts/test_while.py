# This is a simple program to run since it doesn't
# have functions or classes which can be complicated
# and very a bit from version to version.

# It tests operations SETUP_LOOP, GET_ITER, FOR_ITER, LOAD_NAME
"""This program is self-checking!"""

# Compute a triangle
i = j = 1
while i < 5:
    j *= i
    i += 1

assert i == 5
assert j == 24

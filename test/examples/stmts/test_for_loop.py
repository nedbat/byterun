# This is a simple program to run since it doesn't
# have functions or classes which can be complicated
# and very a bit from version to version.

# It tests operations SETUP_LOOP, GET_ITER, FOR_ITER, LOAD_NAME
"""This program is self-checking!"""

out = ""
for i in ["0", "1", "2", "3", "4"]:
    out = out + i
assert out == "01234"

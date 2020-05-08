# Test various kinds of comprehensions.
# In various Pythons there is this .0 parameter
# which isn't listed in the signature by inpsect.
"""This program is self-checking!"""

x = [z*z for z in range(5)]
assert x == [0, 1, 4, 9, 16]

x = {z:z*z for z in range(5)}
assert x == {0:0, 1:1, 2:4, 3:9, 4:16}

x = {z*z for z in range(5)}
assert x == {0, 1, 4, 9, 16}

# This is adapted from uncompyle6's test suite.
# Tests Python's map and unpack syntax.
#
# See Python 3.5+ PEP 448 - Additional Unpacking Generalizations for dictionaries

# Tests opcodes:
#   BUILD_MAP, BUILD_MAP_UNPACK, BUILD_LIST, BUILD_LIST_UNPACK, and BUILD_CONST_KEY_MAP

"""This program is self-checking!"""

b = {**{}}
assert b == {}
c = {**{'a': 1, 'b': 2}}
assert c == {'a': 1, 'b': 2}
d = {**{'x': 1}, **{'y': 2}}
assert d == {'x': 1, 'y': 2}
[*[]]

assert {0: 0} == {**{0:0 for a in c}}

{**{}, **{}}
assert {} == {**{}, **{}, **{}}

{**{}, **{}, **{}}
assert {} == {**{}, **{}, **{}}

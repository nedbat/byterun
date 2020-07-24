# Test various kinds of comparisons
# This originally from byterun was adapted from test_base.py
"""This program is self-checking!"""

assert "x" in "xyz"
assert "x" not in "abc"
assert "x" in ("x", "y", "z")
assert "x" not in ("a", "b", "c")

assert 1 < 3
assert 1 <= 2 and 1 <= 1
assert "a" < "b"
assert "a" <= "b" and "a" <= "a"

assert 3 > 1
assert 3 >= 1 and 3 >= 3
assert "z" > "a"
assert "z" >= "a" and "z" >= "z"


# test JUMP_IF_TRUE_OR_POP
def f(a, b):
    return a or b
assert f(17, 0) == 17
assert f(0, 23) == 23
assert f(0, "") == ""

# test jUMP_IF_FALSE_OR_POP
def f1(a, b):
    return not(a and b)
assert f1(17, 0) is True
assert f1(0, 23) is True
assert f1(0, "") is True
assert f1(17, 23) is False

# test POP_JUMP_IF_TRUE:
def f2(a):
    if not a:
        return 'foo'
    else:
        return 'bar'
assert f2(0) == 'foo'
assert f2(1) == 'bar'

# Test slice assignment
l = list(range(6))

l[2:5] = ["x"]
assert l == [0, 1, 'x', 5]

l = list(range(7))
l[:5] = ["x"]
assert l == ['x', 5, 6]

l = list(range(6))
l[2:] = ["x"]
assert l == [0, 1, 'x']

l = list(range(6))
l[:] = ["x"]
assert l == ['x']

# Test slice deletion

l = list(range(6))
del l[2:5]
assert l == [0, 1, 5]

l = list(range(6))
del l[:5]
assert l == [5]

l = list(range(6))
del l[2:]
assert l == [0, 1]

l = list(range(6))
del l[:]
assert l == []

l = list(range(6))
del l[::2]
assert l == [1, 3, 5]

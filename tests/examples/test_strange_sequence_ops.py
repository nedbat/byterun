# from stdlib: test/test_augassign.py
x = [1,2]
x += [3,4]
x *= 2

assert x == [1, 2, 3, 4, 1, 2, 3, 4]

x = [1, 2, 3]
y = x
x[1:2] *= 2
y[1:2] += [1]

assert x == [1, 2, 1, 2, 3]
assert x is y

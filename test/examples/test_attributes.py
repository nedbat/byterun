l = lambda: 1   # Just to have an object...
l.foo = 17
print(hasattr(l, "foo"), l.foo)
del l.foo
print(hasattr(l, "foo"))

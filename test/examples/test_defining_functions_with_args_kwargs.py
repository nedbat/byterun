# Various functions

# Some Python's like 3.4 are irregular with the order in showing
# dictionary keys. For testing we need them to always come out in the
# same order.
def print_dict_sorted(mydict):
    for key, value in sorted(mydict.items(), key=lambda item: item[1]):
        print("\t%s: %s" % (key, value))
    print("")


def fn(*args):
    print("args is %r" % (args,))


fn(1, 2)


def fn(**kwargs):
    print("kwargs is")
    print_dict_sorted(kwargs)


fn(red=True, blue=False)


def fn(*args, **kwargs):
    print("args is %r" % (args,))
    print("kwargs is:")
    print_dict_sorted(kwargs)


fn(1, 2, red=True, blue=False)


def fn(x, y, *args, **kwargs):
    print("x is %r, y is %r" % (x, y))
    print("args is %r" % (args,))
    print("kwargs is")
    print_dict_sorted(kwargs)


fn("a", "b", 1, 2, red=True, blue=False)

def fn(*args):
    print("args is %r" % (args,))
fn(1, 2)

def fn(**kwargs):
    print("kwargs is %r" % (kwargs,))
fn(red=True, blue=False)

def fn(*args, **kwargs):
    print("args is %r" % (args,))
    print("kwargs is %r" % (kwargs,))
fn(1, 2, red=True, blue=False)

def fn(x, y, *args, **kwargs):
    print("x is %r, y is %r" % (x, y))
    print("args is %r" % (args,))
    print("kwargs is %r" % (kwargs,))
fn('a', 'b', 1, 2, red=True, blue=False)

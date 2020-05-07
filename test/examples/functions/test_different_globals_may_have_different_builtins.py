"""This program is self-checking!"""

def replace_globals(f, new_globals):
    import sys

    if sys.version_info.major == 2:
        args = [
            f.func_code,
            new_globals,
            f.func_name,
            f.func_defaults,
            f.func_closure,
        ]
    else:
        args = [
            f.__code__,
            new_globals,
            f.__name__,
            f.__defaults__,
            f.__closure__,
        ]
    if hasattr(f, "_vm"):
        name = args.remove(args[2])
        args.insert(0, name)
        args.append(f._vm)
    return type(lambda: None)(*args)


def f():
    assert g() == 2
    assert a == 1


def g():
    return a  # a is in the builtins and set to 2


# g and f have different builtins that both provide ``a``.
g = replace_globals(g, {"__builtins__": {"a": 2}})
f = replace_globals(f, {"__builtins__": {"a": 1}, "g": g})


f()

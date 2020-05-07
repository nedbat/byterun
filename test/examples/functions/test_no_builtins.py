# Tests a bug where a function doesn't get
# builtin-functions

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
    if hasattr(f, '_vm'):
        name = args.remove(args[2])
        args.insert(0, name)
        args.append(f._vm)
    return type(lambda: None)(*args)


def f(NameError=NameError, AssertionError=AssertionError):
    # capture NameError and AssertionError early because
    #  we are deleting the builtins
    None
    try:
        sum
    except NameError:
        pass
    else:
        raise AssertionError('sum in the builtins')


f = replace_globals(f, {})  # no builtins provided
f()

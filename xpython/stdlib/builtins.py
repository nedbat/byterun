"""
Compatiability of built-in functions between different Python versions
"""

from typing import Any, Callable
from xdis.version_info import PYTHON_VERSION_TRIPLE

if PYTHON_VERSION_TRIPLE >= (3, 0):
    from builtins import input
    from functools import reduce
    from imp import reload
    import importlib

    import_fn = importlib.__import__
    from io import open
    from sys import intern
else:
    import_fn = __import__


def make_compatible_builtins(builtins: dict, target_python: tuple):
    """
    Add functions in builtins dictionary with functions that do the same
    thing.

    This is needed when doing cross-bytecode interpretation
    because the list of builtin functions varies between different Python versions.
    """
    if not type(target_python) is tuple:
        target_python=(int(str(target_python)[0]),int(str(target_python)[2]))
    short_name = "builtins_%s%s" % (target_python[0], target_python[1])
    import_name = "xpython.stdlib.%s" % short_name
    try:
        module_root = import_fn(import_name)
    except Exception:
        return
    if hasattr(module_root, "stdlib"):
        stdlib_mod = getattr(module_root, "stdlib")
        if hasattr(stdlib_mod, short_name):
            module = getattr(stdlib_mod, short_name)
            needs_compat = module.builtins - builtins.keys()
            for builtin_name in needs_compat:
                if builtin_name in compatable_fns:
                    # print("XXX", builtin_name)
                    builtins[builtin_name] = compatable_fns[builtin_name]
                else:
                    print(
                        "FIXME: add %s-compatible builtin function for %s Python %s\n" %
                        (target_python, target_python, PYTHON_VERSION_TRIPLE[:2])
                    )


def apply(f: Callable, args=None, kwargs=None) -> Any:
    """
    Python 1-2.x apply for Python 3.x
    """
    return f(*args, **kwargs)


def breakpoint(*args, **kwargs):
    """
    Python Python 3.8- breakpoint (compare) for Python 3.x
    """
    print("Not implmeneted yet")


def cmp(x, y) -> int:
    """
    Python 1-2.x cmp (compare) for Python 3.x
    """
    return (x > y) - (x < y)


numeric_types = (int, float, complex)


def coerce(x, y) -> tuple:
    """
    Python 1-2.x coerce for Python 3.x
    """
    if not isinstance(x, numeric_types):
        raise TypeError("number coercion failed")
    if not isinstance(y, numeric_types):
        raise TypeError("number coercion failed")
        raise TypeError
    # Leave unchanged and other operations do the coercion
    return x, y


def execfile(path: str):
    """
    Python 1-2.x execfile for Python 3.x
    """
    exec(compile(open(path).read()))


class OverflowWarning(RuntimeError):
    """A Python 1.x - 2.6 RuntimeError."""

    def __str__(self):
        return "OverflowError: Numerical result out of range"


# Mapping of builtin function name (a str) to a function that implements it compatibly
compatable_fns = {
    "apply": apply,  # Python 1.x-2.x
    "basestring": str,  # Python 1.x-2.x
    "breakpoint": breakpoint,  # Python 1.x-3.7
    "buffer": memoryview,  # Python 1.x-2.x
    "cmp": cmp,  # Python 1.x-2.x
    "coerce": coerce,  # Python 1.x-2.x
    "execfile": execfile,  # Python 1.x-2.x
    "file": open,  # Python 1.x-2.x. Do we eneed to worry about open() mode "rb", vs "rt"?
    "intern": intern,  # Python 1.x-2.x
    "long": int,  # Python 1.x-2.x
    "reduce": reduce,  # Python 1.x-2.x
    "reload": reload,  # Python 1.x-2.x
    "raw_input": input,  # Python 1.x-2.x
    "unichr": chr,  # Python 1.x-2.x
    "unicode": str,  # Python 1.x-2.x
    "xrange": range,  # Python 1.x-2.x
    "OverflowWarning": OverflowWarning,  # Python 1.x-2.6
    "StandardError": Exception,  # Python 1.x-2.x
}

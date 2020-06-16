"""
A place to implement built-in functions.

We use the bytecode for these when doing cross-version interpreting
"""

from xpython.pyobj import Function, Cell, make_cell
from xdis import codeType2Portable, PYTHON_VERSION, IS_PYPY


def func_code(func):
    if hasattr(func, "func_code"):
        return func.func_code
    else:
        assert hasattr(func, "__code__"), "%s should be a function type; is %s" % (
            func,
            type(func),
        )
        return func.__code__


# This code was originally written by Darius Bacon,
# but follows code from PEP 3115 listed below.
# Rocky Bernstein did the xdis adaptions and
# added a couple of bug fixes.


def build_class(opc, func, name, *bases, **kwds):
    """
    Like built-in __build_class__() in bltinmodule.c, but running in the
    byterun VM.

    See also: PEP 3115: https://www.python.org/dev/peps/pep-3115/ and
    https://mail.python.org/pipermail/python-3000/2007-March/006338.html
    """

    # Parameter checking...
    if not (isinstance(func, Function)):
        raise TypeError("func must be a PyVM function")
    if not isinstance(name, str):
        raise TypeError("name is not a string")

    metaclass = kwds.pop("metaclass", None)

    if metaclass is None:
        metaclass = type(bases[0]) if bases else type
    if isinstance(metaclass, type):
        metaclass = calculate_metaclass(metaclass, bases)

    if hasattr(metaclass, "__prepare__"):
        prepare = metaclass.__prepare__
        namespace = prepare(name, bases, **kwds)
    else:
        namespace = {}

    python_implementation = "PyPy" if IS_PYPY else "CPython"

    if not (
        opc.version == PYTHON_VERSION
        and python_implementation == opc.python_implementation
    ):
        # convert code to xdis's portable code type.
        class_body_code = codeType2Portable(func_code(func))
    else:
        class_body_code = func.func_code

    # Execute the body of func. This is the step that would go wrong if
    # we tried to use the built-in __build_class__, because __build_class__
    # does not call func, it magically executes its body directly, as we
    # do here (except we invoke our PyVM instead of CPython's).
    #
    # This behavior when interpreting bytecode that isn't the same as
    # the bytecode using in the running Python can cause a SEGV, specifically
    # between Python 3.5 running 3.4 or earlier.
    frame = func._vm.make_frame(
        code=class_body_code,
        f_globals=func.func_globals,
        f_locals=namespace,
        closure=func.__closure__,
    )

    # rocky: cell is the return value of a function where?
    cell = func._vm.eval_frame(frame)

    # Add any class variables that may have been added in running class_body_code.
    # See test_attribute_access.py for a simple example that needs the update below.
    namespace.update(frame.f_locals)

    # If metaclass is builtin "type", it can't deal with a xpython.pyobj.Cell object
    # but needs a builtin cell object. make_cell() can do this.
    if "__classcell__" in namespace and metaclass == type:
        namespace["__classcell__"] = make_cell(namespace["__classcell__"].get())
    cls = metaclass(name, bases, namespace)
    if isinstance(cell, Cell):
        cell.set(cls)
    return cls


# From Pypy 3.6
# def find_metaclass(bases, namespace, globals, builtin):
#     if '__metaclass__' in namespace:
#         return namespace['__metaclass__']
#     elif len(bases) > 0:
#         base = bases[0]
#         if hasattr(base, '__class__'):
#             return base.__class__
#         else:
#             return type(base)
#     elif '__metaclass__' in globals:
#         return globals['__metaclass__']
#     else:
#         try:
#             return builtin.__metaclass__
#         except AttributeError:
#             return type


def calculate_metaclass(metaclass, bases):
    "Determine the most derived metatype."
    winner = metaclass
    for base in bases:
        t = type(base)
        if issubclass(t, winner):
            winner = t
        elif not issubclass(winner, t):
            raise TypeError("metaclass conflict", winner, t)
    return winner

# This code was written by Darius Bacon
from xpython.pyobj import Function, Cell
from xdis import PYTHON_VERSION, IS_PYPY # , codeType2Portable
from xdis.codetype import codeType2Portable  # until next xdis release

def build_class(opc, func, name, *bases, **kwds):
    """
    Like built-in __build_class__() in bltinmodule.c, but running in the
    byterun VM.
    """

    # Parameter checking...
    if not isinstance(func, Function):
        raise TypeError("func must be a function")
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

    if not (opc.version == PYTHON_VERSION and python_implementation == opc.python_implementation):
        # convert code to xdis's portable code type.
        func_code = codeType2Portable(func.func_code)
    else:
        func_code = func.func_code

    # Execute the body of func. This is the step that would go wrong if
    # we tried to use the built-in __build_class__, because __build_class__
    # does not call func, it magically executes its body directly, as we
    # do here (except we invoke our PyVM instead of CPython's).
    frame = func._vm.make_frame(
        code=func_code, f_globals=func.func_globals, f_locals=namespace
    )

    # rocky: cell is the return value of a function where?
    cell = func._vm.run_frame(frame)

    cls = metaclass(name, bases, namespace)
    if isinstance(cell, Cell):
        cell.set(cls)
    return cls


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

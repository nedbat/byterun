"""Implementations of Python fundamental objects for xpython."""
from __future__ import print_function

import collections
import inspect
import linecache
import types
from copy import copy
from sys import stderr
from xdis import CO_GENERATOR, CO_ITERABLE_COROUTINE, iscode, PYTHON3, PYTHON_VERSION
if PYTHON_VERSION >= 3.4:
    from xpython.stdlib.types34 import _AsyncGeneratorWrapper
else:
    class _AsyncGeneratorWrapper():
        pass

import xpython.stdlib.inspect3 as inspect3
import xpython.stdlib.inspect2 as inspect2

import six

PY2 = not PYTHON3


def make_cell(value):
    # Thanks to Alex Gaynor for help with this bit of twistiness.
    # Construct an actual cell object by creating a closure right here,
    # and grabbing the cell object out of the function we create.
    fn = (lambda x: lambda: x)(value)
    if PYTHON3:
        return fn.__closure__[0]
    else:
        return fn.func_closure[0]


# It might be the case that this is more useful in Python 2.x
# which doesn't seem to show traceback of interpreted code.
# Python 3.x does this but it also shows junk at the end.
Traceback = collections.namedtuple("_Traceback", "tb_frame tb_lasti tb_lineno tb_next")
try:
    _Traceback.tb_frame.__doc__ = "frame object at this level"
    _Traceback.tb_lasti.__doc__ = "index of last attempted instruction in bytecode"
    _Traceback.tb_lineno.__doc__ = "current line number in Python source code"
    _Traceback.tb_next.__doc__ = "next inner traceback object (called by this level)"
except:
    pass


# Code with these names have an implicit .0 in them
COMPREHENSION_FN_NAMES = frozenset(
    ("<setcomp>", "<dictcomp>", "<listcomp>", "<genexpr>",)
)


class Function(object):
    """Function(name, code, globals, argdefs, closure, vm,  kwdefaults={},
                annotations={}, doc=None, qualname=None)

    Create a function object in vm from a code object and a dictionary.
    The name string overrides the name from the code object.
    The optional argdefs tuple specifies the default argument values.
    The optional closure tuple supplies the bindings for free variables.

    In contrast to `types.Function`, parameters appear in the order
    the CPython generates them; also there is an additional parameter
    `vm` which appears last.

    As a convenience, in contrast to types.FunctionType we allow
    setting `kwdefaults` and `annotations`.

    Parameter vm should always be set. The caller should also set __qualname__
    as appropriate.
    """

    __slots__ = [
        "func_code",  # Python 2.x
        "func_name",
        "func_defaults",
        "func_closure",
        "__code__",  # Python 3.x
        "__name__",
        "__defaults__",
        "__kwdefaults__",
        "__closure__",
        # rest
        "func_globals",
        "func_locals",
        "func_dict",
        "__dict__",
        # "__doc__" is filled in by the doc comment above.
        "_vm",
        "_func",
    ]

    def __init__(
        self,
        name,
        code,
        globs,
        argdefs,
        closure=None,
        vm=None,
        kwdefaults={},
        annotations={},
        doc=None,
        qualname=None,
    ):
        self._vm = vm
        self.version = vm.version
        self.__doc__ = doc

        if not name is None and not isinstance(name, str):
            raise TypeError(
                "Function() argument 1 (name) must None or string, not %s" % type(name)
            )

        if not iscode(code):
            raise TypeError(
                "Function() argument 2 (code) must be code, not %s" % type(code)
            )

        if not isinstance(globs, dict):
            raise TypeError(
                "Function() argument 3 (argdefs) must be dict, not %s" % type(globs)
            )

        if closure is not None and not isinstance(closure, tuple):
            raise TypeError(
                "Function() argument 5 (closure) must None or tuple, not %s"
                % type(closure)
            )

        if not vm:
            raise TypeError("Function() argument 6 (vm) must be passed")

        # Function field names below change between Python 2.7 and 3.x.
        # We create attributes for both names. Other code in this file assumes
        # 2.7ish names, while bytecode for 3.x will use 3.x names.
        # TODO: be more stringent based on vm version.
        self.func_code = self.__code__ = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = self.__defaults__ = tuple(argdefs) if argdefs else tuple()
        self.func_closure = self.__closure__ = closure

        self.func_globals = globs
        self.func_locals = vm.frame.f_locals
        self.__dict__ = {
            "version": vm.version,
            "_vm": vm,
        }

        self.__doc__ = (
            code.co_consts[0] if hasattr(code, "co_consts") and code.co_consts else None
        )

        if vm.version >= 3.0:
            self.__annotations__ = annotations
            self.__kwdefaults__ = kwdefaults
            if vm.version >= 3.4:
                self.__qualname__ = qualname if qualname else self.__name__
            else:
                assert qualname is None
        else:
            assert annotations == {}
            assert kwdefaults == {}

        # In Python 3.x is varous generators and list comprehensions have a .0 arg
        # but inspect doesn't show that. In the various MAKE_FUNCTION routines,
        # we will detect this and store True in this field when appropriate.
        if not argdefs and self.__name__.split(".")[-1] in COMPREHENSION_FN_NAMES:
            self.has_dot_zero = True
        else:
            self.has_dot_zero = False

        # From byterun.py:
        #   Sometimes, we need a real Python function. This is for that.
        #
        #
        # An elaboration of the above pity comment may be helpful.
        # Until this project emulates more functions, we rely heavily
        # on some built-in, or standard library
        # functions. `__build_class__` is an example of a builtin;
        # `import` is another example.  Many of Python's standard
        # library inspect routines require native functions, not our
        # emulated classes and types.
        #
        # For the `inspect` module, we've started providing equivalent
        # alternatives, but overall more of this needs to be done.
        #
        # The intent in providing native functions is for use in type
        # testing, mostly. The functios should not be run, since that defeats our
        # ability to trace functions.
        kw = {
            "argdefs": self.func_defaults,
        }
        if closure:
            kw["closure"] = tuple(make_cell(0) for _ in closure)

        if not isinstance(code, types.CodeType) and hasattr(code, "to_native"):
            try:
                code = code.to_native()
            except:
                pass

        if isinstance(code, types.CodeType):
            try:
                self._func = types.FunctionType(code, globs, **kw)
                if vm.version >= 3.0:
                    # Above, types.FunctionType() above doesn't allow passing
                    # in the following attributes, so we set them as
                    # assignments below.
                    self._func.__kwdefaults__ = kwdefaults
                    self._func.__annotations__ = annotations
                    pass
            except:
                self._func = None
        else:
            # cross version interpreting... FIXME: fix this up
            self._func = None

    def __repr__(self):  # pragma: no cover
        return "<Function %s at 0x%08x>" % (self.func_name, id(self))

    def __get__(self, instance, owner):
        if instance is not None:
            return Method(instance, owner, self)
        version = self.version if hasattr(self, "version") else PYTHON_VERSION
        if version < 3.0:
            return Method(None, owner, self)
        else:
            return self

    def __call__(self, *args, **kwargs):
        if self.has_dot_zero:
            # D'oh! http://bugs.python.org/issue19611 Py2 doesn't know how to
            # inspect set comprehensions, dict comprehensions, or generator
            # expressions properly.  They are always functions of one argument,
            # so just do the right thing.
            assert len(args) == 1 and not kwargs, "Surprising comprehension!"
            callargs = {".0": args[0]}
        elif self._func and self.version == PYTHON_VERSION:
            # Perhaps this branch can go and we just use the others.
            # It will require a *lot* more code from inspect.py to be added:
            # classes Signature, Parameter, etc.
            callargs = inspect.getcallargs(self._func, *args, **kwargs)
        else:
            if self.version >= 3.0:
                callargs = inspect3.getcallargs(self, *args, **kwargs)
            else:
                callargs = inspect2.getcallargs(self, *args, **kwargs)

        frame = self._vm.make_frame(
            self.func_code, callargs, self.func_globals, {}, self.__closure__
        )
        if self.__code__.co_flags & CO_GENERATOR:
            qualname = self.__qualname__ if self._vm.version >= 3.4 else None
            gen = Generator(
                g_frame=frame, name=self.__name__, qualname=qualname, vm=self._vm
            )
            if self.__code__.co_flags & CO_ITERABLE_COROUTINE:
                gen = _AsyncGeneratorWrapper(gen)
                frame.generator = gen
                return gen

            frame.generator = gen
            retval = gen
        else:
            retval = self._vm.eval_frame(frame)
        return retval


# FIXME: go over. Not sure how close This is supposed to be
# like type.MethodType
class Method(object):
    """Create a bound instance method object."""

    def __init__(self, obj, _class, func):
        self.__doc__ = obj.__doc__
        self.im_self = obj
        self.im_class = _class
        self.im_func = func

        if hasattr(func, "func_code"):
            self.func_code = func.func_code
        if hasattr(func, "__name__"):
            self.__name__ = func.__name__
        if hasattr(func, "__code__"):
            self.__code__ = func.__code__

        # This causes failure
        # self.__name__ = obj.__name__

    def __repr__(self):  # pragma: no cover
        name = "%s.%s" % (self.im_class.__name__, self.im_func.func_name)
        if self.im_self is not None:
            return "<Bound Method %s of %s>" % (name, self.im_self)
        else:
            return "<Unbound Method %s>" % (name,)

    def __call__(self, *args, **kwargs):
        if self.im_self is not None:
            return self.im_func(self.im_self, *args, **kwargs)
        else:
            return self.im_func(*args, **kwargs)


class Cell(object):
    """A fake cell for closures.

    Closures keep names in scope by storing them not in a frame, but in a
    separate object called a cell.  Frames share references to cells, and
    the LOAD_DEREF and STORE_DEREF opcodes get and set the value from cells.

    This class acts as a cell, though it has to jump through two hoops to make
    the simulation complete:

        1. In order to create actual FunctionType functions, we have to have
           actual cell objects, which are difficult to make. See the twisty
           double-lambda in __init__.

        2. Actual cell objects can't be modified, so to implement STORE_DEREF,
           we store a one-element list in our cell, and then use [0] as the
           actual value.

    """

    def __init__(self, value):
        self.contents = value

    def get(self):
        return self.contents

    def set(self, value):
        self.contents = value


class Block(object):
    """
    Block(type, handler, level)

    The equivalent of CPython's PyFrame_BlockSetup()

    The are used in "try" and "with" statements; before Python 3.8 also in opcodes
    associated with `for` (`SETUP_LOOP`) and `except` (`SETUP_EXCEPT`).

    From Python Include/frameobject.h:

    int b_type;                 /* what kind of block this is */
    int b_handler;              /* where to jump to find handler */
    int b_level;                /* value stack level to pop to */

    """

    def __init__(self, type, handler, level):
        self.type = type
        self.handler = handler
        self.level = level
        return

    def __repr__(self):
        if self.handler is None:
            return "<Block type: %s, stack level: %d" % (self.type, self.level)
        else:
            return "<Block type: %s, end offset: @%d, stack level: %d" % (
                self.type,
                self.handler,
                self.level,
            )


class Frame(object):
    def __init__(
        self, f_code, f_globals, f_locals, f_back, version=PYTHON_VERSION, closure=None
    ):
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = f_back
        self.stack = []
        self.f_trace = None

        if f_back and f_back.f_globals is f_globals:
            # If we share the globals, we share the builtins.
            self.f_builtins = f_back.f_builtins
        else:
            try:
                self.f_builtins = f_globals["__builtins__"]
                if hasattr(self.f_builtins, "__dict__"):
                    self.f_builtins = self.f_builtins.__dict__
            except KeyError:
                # No builtins! Make up a minimal one with None.
                self.f_builtins = {"None": None}

        self.f_lineno = f_code.co_firstlineno

        # Python 2.2.3 initializes this to 0. But by 2.4.6 it is initialized to -1.
        # Note that this has to be coordinated with parse_byte_and_args() of pyvm.py
        # and other places which is why we don't set it to the more correct -1.
        self.f_lasti = -1

        if f_code.co_cellvars:
            self.cells = {}
            if not f_back.cells:
                f_back.cells = {}
            for var in f_code.co_cellvars:
                # Make a cell for the variable in our locals, or None.
                cell = Cell(self.f_locals.get(var))
                f_back.cells[var] = self.cells[var] = cell
        else:
            self.cells = None

        if f_code.co_freevars:
            if not self.cells:
                self.cells = {}
            for i, var in enumerate(f_code.co_freevars):
                if closure:
                    # print("XXX", f_code.co_freevars[i], closure[i].get())
                    # if f_code.co_freevars[i] == "c" and  closure[i].get() == 5:
                    #     from trepan.api import debug; debug()
                    self.cells[var] = closure[i]
                else:
                    # FIXME: this branch is probably wrong.
                    # Also check all calls of Frame and make_frame() in vm to ensure we pass a function's
                    # closure attribute.
                    assert isinstance(f_back.cells[i], Cell), "f_back.cells[%d]: %r" % (
                        i,
                        f_back.cells[i],
                    )
                    self.cells[var] = f_back.cells[var]
                pass
            pass

        self.block_stack = []
        self.generator = None
        self.version = version

        # These are sentinal or bogus values to start out.
        # eval_frame will adjust inst_index.
        self.inst_index = -1
        self.fallthrough = False
        self.last_op = None
        return

    def __repr__(self):  # pragma: no cover
        return "<Frame at 0x%08x: %r:%d @%d>" % (
            id(self),
            self.f_code.co_filename,
            self.f_lineno,
            self.f_lasti,
        )

    def line_number(self):
        """Get the current line number the frame is executing."""
        # We don't keep f_lineno up to date, so calculate it based on the
        # instruction address and the line number table.
        lnotab = self.f_code.co_lnotab
        byte_increments = six.iterbytes(lnotab[0::2])
        line_increments = six.iterbytes(lnotab[1::2])

        byte_num = 0
        line_num = self.f_code.co_firstlineno

        for byte_incr, line_incr in zip(byte_increments, line_increments):
            if isinstance(byte_incr, str):
                return ord(byte_incr)

            byte_num += byte_incr
            if byte_num > self.f_lasti:
                break
            line_num += line_incr

        return line_num


class Traceback(object):
    def __init__(self, frame):
        self.tb_next = frame.f_back
        self.tb_lasti = frame.f_lasti
        self.tb_lineno = frame.f_lineno
        self.tb_frame = frame

    # Note: this can be removed when we have our own compatibility traceback.
    def print_tb(self, limit=None, file=stderr):
        """Like traceback.tb, but is a method."""
        tb = self
        while tb:
            f = tb.tb_frame
            filename = f.f_code.co_filename
            lineno = f.line_number()
            print(
                '  File "%s", line %d, in %s' % (filename, lineno, f.f_code.co_name),
                file=file,
            )
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            if line:
                print("    " + line.strip(), file=file)
            tb = tb.tb_next


def traceback_from_frame(frame):
    tb = None

    while frame:
        next_tb = Traceback(copy(frame))
        next_tb.tb_next = tb
        tb = next_tb
        frame = frame.f_back
    return tb


class Generator(object):
    def __init__(self, g_frame, name, qualname, vm):
        self.gi_frame = g_frame
        self.vm = vm
        self.name = vm
        self.started = False
        self.finished = False
        self.gi_running = False
        self.gi_code = g_frame.f_code
        self.__name__ = g_frame.f_code.co_name
        self.__qualname__ = qualname if g_frame.version >= 3.4 else None

    def __iter__(self):
        return self

    def next(self):
        return self.send(None)

    def send(self, value=None):
        if not self.started and value is not None:
            raise TypeError("Can't send non-None value to a just-started generator")
        self.gi_frame.stack.append(value)
        self.started = True
        self.running = True
        val = self.vm.resume_frame(self.gi_frame)
        if self.finished:
            self.running = False
            raise StopIteration(val)
        return val

    __next__ = next


if __name__ == "__main__":
    # frame = Frame(
    #     traceback_from_frame.__code__,
    #     globals(),
    #     locals(),
    #     None,
    #     PYTHON_VERSION
    # )
    # print(frame)

    class Foo(object):
        "Class Foo docstring"

        def bar(self):
            "This is a docstring"
            return

    foo = Foo()
    myMfoo = Method(foo.bar, Foo, Foo.bar)
    Mfoo = types.MethodType(foo.bar, Foo)
    # Should __name__, _func and __self__ match?
    for attr in "__doc__".split():
        assert getattr(Mfoo, attr) == getattr(myMfoo, attr), attr

    for attr in "__name__ __doc__ __qualname__".split():
        print(getattr(foo.bar, attr), attr)
        assert getattr(foo.bar, attr) == getattr(myMfoo.im_func, attr), attr

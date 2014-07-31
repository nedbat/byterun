"""Implementations of Python fundamental objects for Byterun."""


# TODO(ampere): Add doc strings and remove this.
# pylint: disable=missing-docstring

import collections
import inspect
import types

import six

PY3, PY2 = six.PY3, not six.PY3


def make_cell(value):
    # Thanks to Alex Gaynor for help with this bit of twistiness.
    # Construct an actual cell object by creating a closure right here,
    # and grabbing the cell object out of the function we create.
    fn = (lambda x: lambda: x)(value)
    if PY3:
        return fn.__closure__[0]
    else:
        return fn.func_closure[0]


class Function(object):
    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__',
        '_vm', '_func',
    ]

    CO_OPTIMIZED = 0x0001
    CO_NEWLOCALS = 0x0002
    CO_VARARGS = 0x0004
    CO_VARKEYWORDS = 0x0008
    CO_NESTED = 0x0010
    CO_GENERATOR = 0x0020
    CO_NOFREE = 0x0040
    CO_FUTURE_DIVISION = 0x2000
    CO_FUTURE_ABSOLUTE_IMPORT = 0x4000
    CO_FUTURE_WITH_STATEMENT = 0x8000
    CO_FUTURE_PRINT_FUNCTION = 0x10000
    CO_FUTURE_UNICODE_LITERALS = 0x20000

    def __init__(self, name, code, globs, defaults, closure, vm):
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.f_locals
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None

        # Sometimes, we need a real Python function.  This is for that.
        kw = {
            'argdefs': self.func_defaults,
        }
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)

    def __repr__(self):         # pragma: no cover
        return '<Function %s at 0x%08x>' % (
            self.func_name, id(self)
        )

    def __get__(self, instance, owner):
        if instance is not None:
            return Method(instance, owner, self)
        if PY2:
            return Method(None, owner, self)
        else:
            return self

    def __call__(self, *args, **kwargs):
        if PY2 and self.func_name in ['<setcomp>', '<dictcomp>', '<genexpr>']:
            # D'oh! http://bugs.python.org/issue19611 Py2 doesn't know how to
            # inspect set comprehensions, dict comprehensions, or generator
            # expressions properly.  They are always functions of one argument,
            # so just do the right thing.
            assert len(args) == 1 and not kwargs, 'Surprising comprehension!'
            callargs = {'.0': args[0]}
        else:
            callargs = inspect.getcallargs(self._func, *args, **kwargs)
        frame = self._vm.make_frame(
            self.func_code, callargs, self.func_globals, self.func_locals
        )
        if self.func_code.co_flags & self.CO_GENERATOR:
            gen = Generator(frame, self._vm)
            frame.generator = gen
            retval = gen
        else:
            retval = self._vm.run_frame(frame)
        return retval


class Class(object):
    """
    The VM level mirror of python class type objects.
    """

    def __init__(self, name, bases, methods, vm):
        self._vm = vm
        self.__name__ = name
        self.__bases__ = bases
        self.__mro__ = self._compute_mro(self)
        self.locals = dict(methods)
        self.locals['__name__'] = self.__name__
        self.locals['__mro__'] = self.__mro__
        self.locals['__bases__'] = self.__bases__

    @classmethod
    def mro_merge(cls, seqs):
        """
        Merge a sequence of MROs into a single resulting MRO.
        This code is copied from the following URL with print statments removed.
        https://www.python.org/download/releases/2.3/mro/
        """
        res = []
        while True:
            nonemptyseqs = [seq for seq in seqs if seq]
            if not nonemptyseqs:
                return res
            for seq in nonemptyseqs:  # find merge candidates among seq heads
                cand = seq[0]
                nothead = [s for s in nonemptyseqs if cand in s[1:]]
                if nothead:
                    cand = None  # reject candidate
                else:
                    break
            if not cand:
                raise TypeError("Illegal inheritance.")
            res.append(cand)
            for seq in nonemptyseqs:  # remove candidate
                if seq[0] == cand:
                    del seq[0]

    @classmethod
    def _compute_mro(cls, c):
        """
        Compute the class precedence list (mro) according to C3.
        This code is copied from the following URL with print statments removed.
        https://www.python.org/download/releases/2.3/mro/
        """
        return tuple(cls.mro_merge([[c]] +
                                   [list(base.__mro__) for base in c.__bases__]
                                   + [list(c.__bases__)]))

    def __call__(self, *args, **kw):
        return self._vm.make_instance(self, args, kw)

    def __repr__(self):         # pragma: no cover
        return '<Class %s at 0x%08x>' % (self.__name__, id(self))

    def resolve_attr(self, name):
        """
        Find an attribute in self and return it raw. This does not handle
        properties or method wrapping.
        """
        for base in self.__mro__:
            # The following code does a double lookup on the dict, however
            # measurements show that this is faster than either a special
            # sentinel value or catching KeyError.
            # Handle both VM classes and python host environment classes.
            if isinstance(base, Class):
                if name in base.locals:
                    return base.locals[name]
            else:
                if name in base.__dict__:
                    # Avoid using getattr so we can handle method wrapping
                    return base.__dict__[name]
        raise AttributeError(
            "%r class has no attribute %r" % (self.__name__, name)
        )

    def __getattr__(self, name):
        val = self.resolve_attr(name)
        # Check if we have a descriptor
        get = getattr(val, '__get__', None)
        if get:
            return get(None, self)
        # Not a descriptor, return the value.
        return val


class Object(object):

    def __init__(self, _class, args, kw):
        # pylint: disable=protected-access
        self._vm = _class._vm
        self._class = _class
        self.locals = {}
        if '__init__' in _class.locals:
            _class.locals['__init__'](self, *args, **kw)

    def __repr__(self):         # pragma: no cover
        return '<%s Instance at 0x%08x>' % (self._class.__name__, id(self))

    def __getattr__(self, name):
        if name in self.locals:
            val = self.locals[name]
        else:
            try:
                val = self._class.resolve_attr(name)
            except AttributeError:
                raise AttributeError(
                    "%r object has no attribute %r" %
                    (self._class.__name__, name)
                )
        # Check if we have a descriptor
        get = getattr(val, '__get__', None)
        if get:
            return get(self, self._class)
        # Not a descriptor, return the value.
        return val

    # TODO(ampere): Does this need a __setattr__ and __delattr__ implementation?


class Method(object):

    def __init__(self, obj, _class, func):
        self.im_self = obj
        self.im_class = _class
        self.im_func = func

    def __repr__(self):         # pragma: no cover
        name = "%s.%s" % (self.im_class.__name__, self.im_func.func_name)
        if self.im_self is not None:
            return '<Bound Method %s of %s>' % (name, self.im_self)
        else:
            return '<Unbound Method %s>' % (name,)

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


Block = collections.namedtuple("Block", "type, handler, level")


class Frame(object):
    """
    An interpreter frame. This contains the local value and block
    stacks and the associated code and pointer. The most complex usage
    is with generators in which a frame is stored and then repeatedly
    reactivated. Other than that frames are created executed and then
    discarded.

    Attributes:
      f_code: The code object this frame is executing.
      f_globals: The globals dict used for global name resolution.
      f_locals: Similar for locals.
      f_builtins: Similar for builtins.
      f_back: The frame above self on the stack.
      f_lineno: The first line number of the code object.
      f_lasti: The instruction pointer. Despite its name (which matches actual
      python frames) this points to the next instruction that will be executed.
      block_stack: A stack of blocks used to manage exceptions, loops, and
      "with"s.
      data_stack: The value stack that is used for instruction operands.
      generator: None or a Generator object if this frame is a generator frame.
    """

    def __init__(self, f_code, f_globals, f_locals, f_back):
        self.f_code = f_code
        self.f_globals = f_globals
        self.f_locals = f_locals
        self.f_back = f_back
        if f_back:
            self.f_builtins = f_back.f_builtins
        else:
            self.f_builtins = f_locals['__builtins__']
            if hasattr(self.f_builtins, '__dict__'):
                self.f_builtins = self.f_builtins.__dict__

        self.f_lineno = f_code.co_firstlineno
        self.f_lasti = 0

        self.cells = {}
        if f_code.co_cellvars:
            if not f_back.cells:
                f_back.cells = {}
            for var in f_code.co_cellvars:
                # Make a cell for the variable in our locals, or None.
                cell = Cell(self.f_locals.get(var))
                f_back.cells[var] = self.cells[var] = cell

        if f_code.co_freevars:
            if not self.cells:
                self.cells = {}
            for var in f_code.co_freevars:
                assert self.cells is not None
                assert f_back.cells, "f_back.cells: %r" % (f_back.cells,)
                self.cells[var] = f_back.cells[var]

        # The stack holding exception and generator handling information
        self.block_stack = []
        # The stack holding input and output of bytecode instructions
        self.data_stack = []
        self.generator = None

    def push(self, *vals):
        """Push values onto the value stack."""
        self.data_stack.extend(vals)

    def __repr__(self):         # pragma: no cover
        return '<Frame at 0x%08x: %r @ %d>' % (
            id(self), self.f_code.co_filename, self.f_lineno
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
            byte_num += byte_incr
            if byte_num > self.f_lasti:
                break
            line_num += line_incr

        return line_num


class Generator(object):

    def __init__(self, g_frame, vm):
        self.gi_frame = g_frame
        self.vm = vm
        self.first = True
        self.finished = False

    def __iter__(self):
        return self

    def next(self):
        if self.finished:
            raise StopIteration

        # Ordinary iteration is like sending None into a generator.
        # Push the value onto the frame stack.
        if not self.first:
            self.gi_frame.push(None)
        self.first = False
        # To get the next value from an iterator, push its frame onto the
        # stack, and let it run.
        val = self.vm.resume_frame(self.gi_frame)
        if self.finished:
            raise StopIteration
        return val

    __next__ = next

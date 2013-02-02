"""Implementations of Python fundamental objects for Byterun."""

import collections, types

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
    def __init__(self, name, code, globs, defaults, closure, vm):
        self.vm = vm
        self.func_code = code
        self.func_name = name or code.co_name
        self.func_defaults = defaults
        self.func_globals = globs
        self.func_dict = vm.frame.f_locals
        self.func_closure = closure

        # Sometimes, we need a real Python function.  This is for that.
        kw = {}
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self.func = types.FunctionType(code, globs, argdefs=tuple(defaults), **kw)

    def __repr__(self):         # pragma: no cover
        return '<function %s at 0x%08X>' % (self.func_name, id(self))

    def __call__(self, *args, **kw):
        if len(args) < self.func_code.co_argcount:
            if not self.func_defaults:
                if self.func_code.co_argcount == 0:
                    argCount = 'no arguments'
                elif self.func_code.co_argcount == 1:
                    argCount = 'exactly 1 argument'
                else:
                    argCount = 'exactly %i arguments' % self.func_code.co_argcount
                raise TypeError('%s() takes %s (%s given)' % (self.func_name,
                                                               argCount, len(args)))
            else:
                defArgCount = len(self.func_defaults)
                args.extend(self.func_defaults[-(self.func_code.co_argcount - len(args)):])
        frame = self.vm.make_frame(self.func_code, args, kw, self.func_globals, self.func_dict)
        return self.vm.run_frame(frame)


class Class(object):
    def __init__(self, name, bases, methods):
        self.name = name
        self.bases = bases
        self.locals = methods

    def __call__(self, *args, **kw):
        return Object(self, self.locals, args, kw)

    def __repr__(self):         # pragma: no cover
        return '<class %s at 0x%08X>' % (self.name, id(self))


class Object(object):
    def __init__(self, _class, methods, args, kw):
        self._class = _class
        self.locals = methods
        if '__init__' in methods:
            methods['__init__'](self, *args, **kw)

    def __repr__(self):         # pragma: no cover
        return '<%s instance at 0x%08X>' % (self._class.name, id(self))

    def __getattr__(self, name):
        try:
            val = self.locals[name]
        except KeyError:
            raise AttributeError("Object %r has no attribute %r" % (self, name))
        if isinstance(val, Function):
            val = Method(self, self._class, val)
        return val


class Method:
    def __init__(self, obj, _class, func):
        self.im_self = obj
        self.im_class = _class
        self.im_func = func

    def __repr__(self):         # pragma: no cover
        name = "%s.%s" % (self.im_class.name, self.im_func.func_name)
        if self.im_self:
            return '<bound method %s of %s>' % (name, self.im_self)
        else:
            return '<unbound method %s>' % (name,)

    def __call__(self, *args, **kwargs):
        return self.im_func(self.im_self, *args, **kwargs)


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
            for var in f_code.co_freevars:
                self.cells[var] = f_back.cells[var]

        self.block_stack = []
        self.generator = None

    def __repr__(self):         # pragma: no cover
        return '<frame object at 0x%08X>' % id(self)


class Generator(object):
    def __init__(self, g_frame, vm):
        self.gi_frame = g_frame
        self.vm = vm

    def __iter__(self):
        self.first = True
        self.finished = False
        return self

    def next(self):
        # Ordinary iteration is like sending None into a generator.
        if not self.first:
            self.vm.push(None)
        self.first = False
        # To get the next value from an iterator, push its frame onto the
        # stack, and let it run.
        val = self.vm.resume_frame(self.gi_frame)
        if self.finished:
            raise StopIteration
        return val
    __next__ = next


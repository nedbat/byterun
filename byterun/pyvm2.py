"""A pure-Python Python bytecode interpreter."""
# Based on:
# pyvm2 by Paul Swartz (z3p), from http://www.twistedmatrix.com/users/z3p/


# Disable because there are enough false positives to make it useless
# pylint: disable=unbalanced-tuple-unpacking
# pylint: disable=unpacking-non-sequence

# TODO(ampere): Add doc strings and remove this.
# pylint: disable=missing-docstring

from __future__ import print_function, division
import dis
import inspect
import linecache
import logging
import operator
import sys

import six
from six.moves import reprlib

from .pyobj import Frame, Block, Method, Object, Function, Class, Generator

log = logging.getLogger(__name__)

PY3, PY2 = six.PY3, not six.PY3

if six.PY3:
    byteint = lambda b: b
else:
    byteint = ord

# Create a repr that won't overflow.
repr_obj = reprlib.Repr()
repr_obj.maxother = 120
repper = repr_obj.repr


class VirtualMachineError(Exception):
    """For raising errors in the operation of the VM."""
    pass


class VirtualMachine(object):

    def __init__(self):
        # The call stack of frames.
        self.frames = []
        # The current frame.
        self.frame = None
        self.return_value = None
        self.last_exception = None
        self.vmbuiltins = dict(__builtins__)
        self.vmbuiltins["isinstance"] = self.isinstance
        # Operator tables. These are overriden by subclasses to replace the
        # meta-cyclic implementations.
        self.unary_operators = {
            'POSITIVE': operator.pos,
            'NEGATIVE': operator.neg,
            'NOT':      operator.not_,
            'CONVERT':  repr,
            'INVERT':   operator.invert,
        }
        self.binary_operators = {
            'POWER':    pow,
            'MULTIPLY': operator.mul,
            'DIVIDE':   getattr(operator, 'div', lambda x, y: None),
            'FLOOR_DIVIDE': operator.floordiv,
            'TRUE_DIVIDE':  operator.truediv,
            'MODULO':   operator.mod,
            'ADD':      operator.add,
            'SUBTRACT': operator.sub,
            'SUBSCR':   operator.getitem,
            'LSHIFT':   operator.lshift,
            'RSHIFT':   operator.rshift,
            'AND':      operator.and_,
            'XOR':      operator.xor,
            'OR':       operator.or_,
        }
        self.compare_operators = [
            operator.lt,
            operator.le,
            operator.eq,
            operator.ne,
            operator.gt,
            operator.ge,
            lambda x, y: x in y,
            lambda x, y: x not in y,
            lambda x, y: x is y,
            lambda x, y: x is not y,
            lambda x, y: issubclass(x, Exception) and issubclass(x, y),
        ]

    def top(self):
        """Return the value at the top of the stack, with no changes."""
        return self.frame.data_stack[-1]

    def pop(self, i=0):
        """Pop a value from the stack.

        Default to the top of the stack, but `i` can be a count from the top
        instead.

        """
        return self.frame.data_stack.pop(-1-i)

    def push(self, *vals):
        """Push values onto the value stack."""
        self.frame.push(*vals)

    def popn(self, n):
        """Pop a number of values from the value stack.

        A list of `n` values is returned, the deepest value first.

        """
        if n:
            ret = self.frame.data_stack[-n:]
            self.frame.data_stack[-n:] = []
            return ret
        else:
            return []

    def peek(self, n):
        """
        Get a value `n` entries down in the stack, without changing the stack.
        """
        return self.frame.data_stack[-n]

    def jump(self, jump):
        """
        Move the bytecode pointer to `jump`, so it will execute next.

        Jump may be the very next instruction and hence already the value of
        f_lasti. This is used to notify a subclass when a jump was not taken and
        instead we continue to the next instruction.
        """
        self.frame.f_lasti = jump

    def push_block(self, type, handler=None, level=None):
        if level is None:
            level = len(self.frame.data_stack)
        self.frame.block_stack.append(Block(type, handler, level))

    def pop_block(self):
        return self.frame.block_stack.pop()

    def make_frame(self, code, callargs={}, f_globals=None, f_locals=None):
        # The callargs default is safe because we never modify the dict.
        # pylint: disable=dangerous-default-value
        log.info("make_frame: code=%r, callargs=%s, f_globals=%r, f_locals=%r",
                 code, repper(callargs), (type(f_globals), id(f_globals)),
                  (type(f_locals), id(f_locals)))
        if f_globals is not None:
            f_globals = f_globals
            if f_locals is None:
                f_locals = f_globals
        elif self.frames:
            f_globals = self.frame.f_globals
            f_locals = {}
        else:
            # TODO(ampere): __name__, __doc__, __package__ below are not correct
            f_globals = f_locals = {
                '__builtins__': self.vmbuiltins,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }

        # Implement NEWLOCALS flag. See Objects/frameobject.c in CPython.
        if code.co_flags & Function.CO_NEWLOCALS:
            f_locals = {}

        f_locals.update(callargs)
        frame = self.make_frame_with_dicts(code, f_globals, f_locals)
        log.info("%r", frame)
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    def print_frames(self):
        """Print the call stack, for debugging."""
        for f in self.frames:
            filename = f.f_code.co_filename
            lineno = f.line_number()
            print('  File "%s", line %d, in %s' % (
                filename, lineno, f.f_code.co_name
            ))
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            if line:
                print('    ' + line.strip())

    def resume_frame(self, frame):
        frame.f_back = self.frame
        log.info("resume_frame: %r", frame)
        val = self.run_frame(frame)
        frame.f_back = None
        return val

    def run_code(self, code, f_globals=None, f_locals=None):
        frame = self.make_frame(code, f_globals=f_globals, f_locals=f_locals)
        val = self.run_frame(frame)
        # Check some invariants
        if self.frames:            # pragma: no cover
            raise VirtualMachineError("Frames left over!")
        if self.frame is not None and self.frame.data_stack:  # pragma: no cover
            raise VirtualMachineError("Data left on stack! %r" %
                                      self.frame.data_stack)

        return val

    def unwind_block(self, block):
        if block.type == 'except-handler':
            offset = 3
        else:
            offset = 0

        while len(self.frame.data_stack) > block.level + offset:
            self.pop()

        if block.type == 'except-handler':
            tb, value, exctype = self.popn(3)
            self.last_exception = exctype, value, tb

    def parse_byte_and_args(self):
        f = self.frame
        opoffset = f.f_lasti
        try:
            byteCode = byteint(f.f_code.co_code[opoffset])
        except IndexError:
            raise VirtualMachineError(
                "Bad bytecode offset %d in %s (len=%d)" %
                (opoffset, str(f.f_code), len(f.f_code.co_code))
            )
        f.f_lasti += 1
        byteName = dis.opname[byteCode]
        arg = None
        arguments = []
        if byteCode >= dis.HAVE_ARGUMENT:
            arg = f.f_code.co_code[f.f_lasti:f.f_lasti+2]
            f.f_lasti += 2
            intArg = byteint(arg[0]) + (byteint(arg[1]) << 8)
            if byteCode in dis.hasconst:
                arg = f.f_code.co_consts[intArg]
            elif byteCode in dis.hasfree:
                if intArg < len(f.f_code.co_cellvars):
                    arg = f.f_code.co_cellvars[intArg]
                else:
                    var_idx = intArg - len(f.f_code.co_cellvars)
                    arg = f.f_code.co_freevars[var_idx]
            elif byteCode in dis.hasname:
                arg = f.f_code.co_names[intArg]
            elif byteCode in dis.hasjrel:
                arg = f.f_lasti + intArg
            elif byteCode in dis.hasjabs:
                arg = intArg
            elif byteCode in dis.haslocal:
                arg = f.f_code.co_varnames[intArg]
            else:
                arg = intArg
            arguments = [arg]

        return byteName, arguments, opoffset

    def log(self, byteName, arguments, opoffset):
        # pylint: disable=logging-not-lazy
        op = "%d: %s" % (opoffset, byteName)
        if arguments:
            op += " %r" % (arguments[0],)
        indent = "    "*(len(self.frames)-1)
        stack_rep = repper(self.frame.data_stack)
        block_stack_rep = repper(self.frame.block_stack)

        log.info("  %sdata: %s" % (indent, stack_rep))
        log.info("  %sblks: %s" % (indent, block_stack_rep))
        log.info("%s%s" % (indent, op))

    def dispatch(self, byteName, arguments):
        why = None
        try:
            if byteName.startswith('UNARY_'):
                self.unaryOperator(byteName[6:])
            elif byteName.startswith('BINARY_'):
                self.binaryOperator(byteName[7:])
            elif byteName.startswith('INPLACE_'):
                self.inplaceOperator(byteName[8:])
            elif 'SLICE+' in byteName:
                self.sliceOperator(byteName)
            else:
                # dispatch
                bytecode_fn = getattr(self, 'byte_%s' % byteName, None)
                if not bytecode_fn:            # pragma: no cover
                    raise VirtualMachineError(
                        "unknown bytecode type: %s" % byteName
                    )
                why = bytecode_fn(*arguments)
        except:  # pylint: disable=bare-except
            # deal with exceptions encountered while executing the op.
            self.last_exception = sys.exc_info()[:2] + (None,)
            log.exception("Caught exception during execution")
            why = 'exception'

        return why

    def manage_block_stack(self, why):
        assert why != 'yield'

        block = self.frame.block_stack[-1]
        if block.type == 'loop' and why == 'continue':
            self.jump(self.return_value)
            why = None
            return why

        self.pop_block()
        self.unwind_block(block)

        if block.type == 'loop' and why == 'break':
            why = None
            self.jump(block.handler)
            return why

        if PY2:
            if (
                block.type == 'finally' or
                (block.type == 'setup-except' and why == 'exception') or
                block.type == 'with'
            ):
                if why == 'exception':
                    exctype, value, tb = self.last_exception
                    self.push(tb, value, exctype)
                else:
                    if why in ('return', 'continue'):
                        self.push(self.return_value)
                    self.push(why)

                why = None
                self.jump(block.handler)
                return why

        elif PY3:
            if (
                why == 'exception' and
                block.type in ['setup-except', 'finally']
            ):
                self.push_block('except-handler')
                exctype, value, tb = self.last_exception
                self.push(tb, value, exctype)
                # PyErr_Normalize_Exception goes here
                self.push(tb, value, exctype)
                why = None
                self.jump(block.handler)
                return why

            elif block.type == 'finally':
                if why in ('return', 'continue'):
                    self.push(self.return_value)
                self.push(why)

                why = None
                self.jump(block.handler)
                return why

        return why

    def run_instruction(self):
        """Run one instruction in the current frame.

        Return None if the frame should continue executing otherwise return the
        reason it should stop.
        """
        frame = self.frame
        byteName, arguments, opoffset = self.parse_byte_and_args()
        if log.isEnabledFor(logging.INFO):
            self.log(byteName, arguments, opoffset)

        # When unwinding the block stack, we need to keep track of why we
        # are doing it.
        why = self.dispatch(byteName, arguments)
        if why == 'exception':
            # TODO: ceval calls PyTraceBack_Here, not sure what that does.
            pass

        if why == 'reraise':
            why = 'exception'

        if why != 'yield':
            while why and frame.block_stack:
                # Deal with any block management we need to do.
                why = self.manage_block_stack(why)

        return why

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.
        """
        self.push_frame(frame)
        while True:
            why = self.run_instruction()
            if why:
                break
        self.pop_frame()

        if why == 'exception':
            six.reraise(*self.last_exception)

        return self.return_value

    ## Builders for objects that subclasses may want to replace with subclasses

    def make_instance(self, cls, args, kw):
        """
        Create an instance of the given class with the given constructor args.
        """
        return Object(cls, args, kw)

    def make_class(self, name, bases, methods):
        """
        Create a class with the name bases and methods given.
        """
        return Class(name, bases, methods, self)

    def make_function(self, name, code, globs, defaults, closure):
        """
        Create a function or closure given the arguments.
        """
        return Function(name, code, globs, defaults, closure, self)

    def make_frame_with_dicts(self, code, f_globals, f_locals):
        """
        Create a frame with the given code, globals, and locals.
        """
        return Frame(code, f_globals, f_locals, self.frame)

    ## Built-in overrides

    def isinstance(self, obj, cls):
        if isinstance(obj, Object):
            # pylint: disable=protected-access
            return issubclass(obj._class, cls)
        elif isinstance(cls, Class):
            return False
        else:
            return isinstance(obj, cls)

    ## Abstraction hooks

    def load_constant(self, value):
        """
        Called when the constant value is loaded onto the stack.
        The returned value is pushed onto the stack instead.
        """
        return value

    def get_locals_dict(self):
        """Get a real python dict of the locals."""
        return self.frame.f_locals

    def get_locals_dict_bytecode(self):
        """Get a possibly abstract bytecode level representation of the locals.
        """
        return self.frame.f_locals

    def set_locals_dict_bytecode(self, lcls):
        """Set the locals from a possibly abstract bytecode level dict.
        """
        self.frame.f_locals = lcls

    def get_globals_dict(self):
        """Get a real python dict of the globals."""
        return self.frame.f_globals

    def load_local(self, name):
        """
        Called when a local is loaded onto the stack.
        The returned value is pushed onto the stack instead of the actual loaded
        value.
        """
        return self.frame.f_locals[name]

    def load_builtin(self, name):
        return self.frame.f_builtins[name]

    def load_global(self, name):
        """
        Same as load_local except for globals.
        """
        return self.frame.f_globals[name]

    def load_deref(self, name):
        """
        Same as load_local except for closure cells.
        """
        return self.frame.cells[name].get()

    def store_local(self, name, value):
        """
        Called when a local is written.
        The returned value is stored instead of the value on the stack.
        """
        self.frame.f_locals[name] = value

    def store_deref(self, name, value):
        """
        Same as store_local except for closure cells.
        """
        self.frame.cells[name].set(value)

    def del_local(self, name):
        """
        Called when a local is deleted.
        """
        del self.frame.f_locals[name]

    def load_attr(self, obj, attr):
        """
        Perform the actual attribute load on an object. This must support all
        objects that may appear in the VM. This defaults to just get attr.
        """
        return getattr(obj, attr)

    def store_attr(self, obj, attr, value):
        """
        Same as load_attr except for setting attributes. Defaults to setattr.
        """
        setattr(obj, attr, value)

    def del_attr(self, obj, attr):
        """
        Same as load_attr except for deleting attributes. Defaults to delattr.
        """
        delattr(obj, attr)

    def build_tuple(self, content):
        """
        Create a VM tuple from the given sequence.
        The returned object must support the tuple interface.
        """
        return tuple(content)

    def build_list(self, content):
        """
        Create a VM list from the given sequence.
        The returned object must support the list interface.
        """
        return list(content)

    def build_set(self, content):
        """
        Create a VM set from the given sequence.
        The returned object must support the set interface.
        """
        return set(content)

    def build_map(self):
        """
        Create an empty VM dict.
        The returned object must support the dict interface.
        """
        return dict()

    def store_subscr(self, obj, subscr, val):
        obj[subscr] = val

    def del_subscr(self, obj, subscr):
        del obj[subscr]

    ## Stack manipulation

    def byte_LOAD_CONST(self, const):
        self.push(self.load_constant(const))

    def byte_POP_TOP(self):
        self.pop()

    def byte_DUP_TOP(self):
        self.push(self.top())

    def byte_DUP_TOPX(self, count):
        items = self.popn(count)
        for i in [1, 2]:
            self.push(*items)

    def byte_DUP_TOP_TWO(self):
        # Py3 only
        a, b = self.popn(2)
        self.push(a, b, a, b)

    def byte_ROT_TWO(self):
        a, b = self.popn(2)
        self.push(b, a)

    def byte_ROT_THREE(self):
        a, b, c = self.popn(3)
        self.push(c, a, b)

    def byte_ROT_FOUR(self):
        a, b, c, d = self.popn(4)
        self.push(d, a, b, c)

    ## Names

    def byte_LOAD_NAME(self, name):
        try:
            val = self.load_local(name)
        except KeyError:
            try:
                val = self.load_global(name)
            except KeyError:
                try:
                    val = self.load_builtin(name)
                except KeyError:
                    raise NameError("name '%s' is not defined" % name)
        self.push(val)

    def byte_STORE_NAME(self, name):
        self.store_local(name, self.pop())

    def byte_DELETE_NAME(self, name):
        self.del_local(name)

    def byte_LOAD_FAST(self, name):
        try:
            val = self.load_local(name)
            log.info("LOAD_FAST: %s from %r -> %r", name, self.frame, val)
        except KeyError:
            raise UnboundLocalError(
                "local variable '%s' referenced before assignment" % name
            )
        self.push(val)

    def byte_STORE_FAST(self, name):
        self.byte_STORE_NAME(name)

    def byte_DELETE_FAST(self, name):
        self.byte_DELETE_NAME(name)

    def byte_LOAD_GLOBAL(self, name):
        try:
            val = self.load_global(name)
        except KeyError:
            try:
                val = self.load_builtin(name)
            except KeyError:
                raise NameError("global name '%s' is not defined" % name)
        self.push(val)

    def byte_LOAD_DEREF(self, name):
        self.push(self.load_deref(name))

    def byte_STORE_DEREF(self, name):
        self.store_deref(name, self.pop())

    def byte_LOAD_LOCALS(self):
        self.push(self.get_locals_dict_bytecode())

    ## Operators

    def unaryOperator(self, op):
        x = self.pop()
        self.push(self.unary_operators[op](x))

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.binary_operators[op](x, y))

    def inplaceOperator(self, op):
        x, y = self.popn(2)
        if op == 'POWER':
            x **= y
        elif op == 'MULTIPLY':
            x *= y
        elif op in ['DIVIDE', 'FLOOR_DIVIDE']:
            x //= y
        elif op == 'TRUE_DIVIDE':
            x /= y
        elif op == 'MODULO':
            x %= y
        elif op == 'ADD':
            x += y
        elif op == 'SUBTRACT':
            x -= y
        elif op == 'LSHIFT':
            x <<= y
        elif op == 'RSHIFT':
            x >>= y
        elif op == 'AND':
            x &= y
        elif op == 'XOR':
            x ^= y
        elif op == 'OR':
            x |= y
        else:           # pragma: no cover
            raise VirtualMachineError("Unknown in-place operator: %r" % op)
        self.push(x)

    def sliceOperator(self, op):
        start = 0
        end = None          # we will take this to mean end
        op, count = op[:-2], int(op[-1])
        if count == 1:
            start = self.pop()
        elif count == 2:
            end = self.pop()
        elif count == 3:
            end = self.pop()
            start = self.pop()
        l = self.pop()
        if end is None:
            end = len(l)
        if op.startswith('STORE_'):
            l[start:end] = self.pop()
        elif op.startswith('DELETE_'):
            del l[start:end]
        else:
            self.push(l[start:end])

    def byte_COMPARE_OP(self, opnum):
        x, y = self.popn(2)
        self.push(self.compare_operators[opnum](x, y))

    ## Attributes and indexing

    def byte_LOAD_ATTR(self, attr):
        obj = self.pop()
        log.info("LOAD_ATTR: %r %s", type(obj), attr)
        val = self.load_attr(obj, attr)
        self.push(val)

    def byte_STORE_ATTR(self, name):
        val, obj = self.popn(2)
        self.store_attr(obj, name, val)

    def byte_DELETE_ATTR(self, name):
        obj = self.pop()
        self.del_attr(obj, name)

    def byte_STORE_SUBSCR(self):
        val, obj, subscr = self.popn(3)
        self.store_subscr(obj, subscr, val)

    def byte_DELETE_SUBSCR(self):
        obj, subscr = self.popn(2)
        self.del_subscr(obj, subscr)

    ## Building

    def byte_BUILD_TUPLE(self, count):
        elts = self.popn(count)
        self.push(self.build_tuple(elts))

    def byte_BUILD_LIST(self, count):
        elts = self.popn(count)
        self.push(self.build_list(elts))

    def byte_BUILD_SET(self, count):
        # TODO: Not documented in Py2 docs.
        elts = self.popn(count)
        self.push(self.build_set(elts))

    def byte_BUILD_MAP(self, size):
        # size is ignored.
        self.push(self.build_map())

    def byte_STORE_MAP(self):
        the_map, val, key = self.popn(3)
        the_map[key] = val
        self.push(the_map)

    def byte_UNPACK_SEQUENCE(self, count):
        seq = self.pop()
        for x in reversed(seq):
            self.push(x)

    def byte_BUILD_SLICE(self, count):
        if count == 2:
            x, y = self.popn(2)
            self.push(slice(x, y))
        elif count == 3:
            x, y, z = self.popn(3)
            self.push(slice(x, y, z))
        else:           # pragma: no cover
            raise VirtualMachineError("Strange BUILD_SLICE count: %r" % count)

    def byte_LIST_APPEND(self, count):
        val = self.pop()
        the_list = self.peek(count)
        the_list.append(val)

    def byte_SET_ADD(self, count):
        val = self.pop()
        the_set = self.peek(count)
        the_set.add(val)

    def byte_MAP_ADD(self, count):
        val, key = self.popn(2)
        the_map = self.peek(count)
        the_map[key] = val

    ## Printing

    if 0:   # Only used in the interactive interpreter, not in modules.
        def byte_PRINT_EXPR(self):
            print(self.pop())

    def byte_PRINT_ITEM(self):
        item = self.pop()
        self.print_item(item)

    def byte_PRINT_ITEM_TO(self):
        to = self.pop()
        item = self.pop()
        self.print_item(item, to)

    def byte_PRINT_NEWLINE(self):
        self.print_newline()

    def byte_PRINT_NEWLINE_TO(self):
        to = self.pop()
        self.print_newline(to)

    def print_item(self, item, to=None):
        if to is None:
            to = sys.stdout
        if to.softspace:
            print(" ", end="", file=to)
            to.softspace = 0
        print(item, end="", file=to)
        if isinstance(item, str):
            if (not item) or (not item[-1].isspace()) or (item[-1] == " "):
                to.softspace = 1
        else:
            to.softspace = 1

    def print_newline(self, to=None):
        if to is None:
            to = sys.stdout
        print("", file=to)
        to.softspace = 0

    ## Jumps

    def byte_JUMP_FORWARD(self, jump):
        self.jump(jump)

    def byte_JUMP_ABSOLUTE(self, jump):
        self.jump(jump)

    if 0:   # Not in py2.7
        def byte_JUMP_IF_TRUE(self, jump):
            val = self.top()
            if val:
                self.jump(jump)
            else:
                self.jump(self.frame.f_lasti)

        def byte_JUMP_IF_FALSE(self, jump):
            val = self.top()
            if not val:
                self.jump(jump)
            else:
                self.jump(self.frame.f_lasti)

    def byte_POP_JUMP_IF_TRUE(self, jump):
        val = self.pop()
        if val:
            self.jump(jump)
        else:
            self.jump(self.frame.f_lasti)

    def byte_POP_JUMP_IF_FALSE(self, jump):
        val = self.pop()
        if not val:
            self.jump(jump)
        else:
            self.jump(self.frame.f_lasti)

    def byte_JUMP_IF_TRUE_OR_POP(self, jump):
        val = self.top()
        if val:
            self.jump(jump)
        else:
            self.pop()
            self.jump(self.frame.f_lasti)

    def byte_JUMP_IF_FALSE_OR_POP(self, jump):
        val = self.top()
        if not val:
            self.jump(jump)
        else:
            self.pop()
            self.jump(self.frame.f_lasti)

    ## Blocks

    def byte_SETUP_LOOP(self, dest):
        self.push_block('loop', dest)

    def byte_GET_ITER(self):
        self.push(iter(self.pop()))

    def byte_FOR_ITER(self, jump):
        iterobj = self.top()
        try:
            v = next(iterobj)
            self.push(v)
            self.jump(self.frame.f_lasti)
        except StopIteration:
            self.pop()
            self.jump(jump)

    def byte_BREAK_LOOP(self):
        return 'break'

    def byte_CONTINUE_LOOP(self, dest):
        # This is a trick with the return value.
        # While unrolling blocks, continue and return both have to preserve
        # state as the finally blocks are executed.  For continue, it's
        # where to jump to, for return, it's the value to return.  It gets
        # pushed on the stack for both, so continue puts the jump destination
        # into return_value.
        self.return_value = dest
        return 'continue'

    def byte_SETUP_EXCEPT(self, dest):
        self.push_block('setup-except', dest)

    def byte_SETUP_FINALLY(self, dest):
        self.push_block('finally', dest)

    def byte_END_FINALLY(self):
        v = self.pop()
        if isinstance(v, str):
            why = v
            if why in ('return', 'continue'):
                self.return_value = self.pop()
            if why == 'silenced':       # PY3
                block = self.pop_block()
                assert block.type == 'except-handler'
                self.unwind_block(block)
                why = None
        elif v is None:
            why = None
        elif issubclass(v, BaseException):
            exctype = v
            val = self.pop()
            tb = self.pop()
            self.last_exception = (exctype, val, tb)
            why = 'reraise'
        else:       # pragma: no cover
            raise VirtualMachineError("Confused END_FINALLY")
        return why

    def byte_POP_BLOCK(self):
        self.pop_block()

    if PY2:
        def byte_RAISE_VARARGS(self, argc):
            # NOTE: the dis docs are completely wrong about the order of the
            # operands on the stack!
            exctype = val = tb = None
            if argc == 0:
                exctype, val, tb = self.last_exception
            elif argc == 1:
                exctype = self.pop()
            elif argc == 2:
                val = self.pop()
                exctype = self.pop()
            elif argc == 3:
                tb = self.pop()
                val = self.pop()
                exctype = self.pop()

            # There are a number of forms of "raise", normalize them somewhat.
            if isinstance(exctype, BaseException):
                val = exctype
                exctype = type(val)

            self.last_exception = (exctype, val, tb)

            if tb:
                return 'reraise'
            else:
                return 'exception'

    elif PY3:
        def byte_RAISE_VARARGS(self, argc):
            cause = exc = None
            if argc == 2:
                cause = self.pop()
                exc = self.pop()
            elif argc == 1:
                exc = self.pop()
            return self.do_raise(exc, cause)

        def do_raise(self, exc, cause):
            if exc is None:         # reraise
                exc_type, val, tb = self.last_exception
                if exc_type is None:
                    return 'exception'      # error
                else:
                    return 'reraise'

            elif type(exc) == type:
                # As in `raise ValueError`
                exc_type = exc
                val = exc()             # Make an instance.
            elif isinstance(exc, BaseException):
                # As in `raise ValueError('foo')`
                exc_type = type(exc)
                val = exc
            else:
                return 'exception'      # error

            # If you reach this point, you're guaranteed that
            # val is a valid exception instance and exc_type is its class.
            # Now do a similar thing for the cause, if present.
            if cause:
                if type(cause) == type:
                    cause = cause()
                elif not isinstance(cause, BaseException):
                    return 'exception'  # error

                val.__cause__ = cause

            self.last_exception = exc_type, val, val.__traceback__
            return 'exception'

    def byte_POP_EXCEPT(self):
        block = self.pop_block()
        if block.type != 'except-handler':
            raise Exception("popped block is not an except handler")
        self.unwind_block(block)

    def byte_SETUP_WITH(self, dest):
        ctxmgr = self.pop()
        self.push(ctxmgr.__exit__)
        ctxmgr_obj = ctxmgr.__enter__()
        if PY2:
            self.push_block('with', dest)
        elif PY3:
            self.push_block('finally', dest)
        self.push(ctxmgr_obj)

    def byte_WITH_CLEANUP(self):
        # The code here does some weird stack manipulation: the exit function
        # is buried in the stack, and where depends on what's on top of it.
        # Pull out the exit function, and leave the rest in place.
        v = w = None
        u = self.top()
        if u is None:
            exit_func = self.pop(1)
        elif isinstance(u, str):
            if u in ('return', 'continue'):
                exit_func = self.pop(2)
            else:
                exit_func = self.pop(1)
            u = None
        elif issubclass(u, BaseException):
            if PY2:
                w, v, u = self.popn(3)
                exit_func = self.pop()
                self.push(w, v, u)
            elif PY3:
                w, v, u = self.popn(3)
                tp, exc, tb = self.popn(3)
                exit_func = self.pop()
                self.push(tp, exc, tb)
                self.push(None)
                self.push(w, v, u)
                block = self.pop_block()
                assert block.type == 'except-handler'
                self.push_block(block.type, block.handler, block.level-1)
        else:       # pragma: no cover
            raise VirtualMachineError("Confused WITH_CLEANUP")
        exit_ret = exit_func(u, v, w)
        err = (u is not None) and bool(exit_ret)
        if err:
            # An error occurred, and was suppressed
            if PY2:
                self.popn(3)
                self.push(None)
            elif PY3:
                self.push('silenced')

    ## Functions

    def byte_MAKE_FUNCTION(self, argc):
        if PY3:
            name = self.pop()
        else:
            name = None
        code = self.pop()
        defaults = self.popn(argc)
        globs = self.get_globals_dict()
        fn = self.make_function(name, code, globs, defaults, None)
        self.push(fn)

    def byte_LOAD_CLOSURE(self, name):
        self.push(self.frame.cells[name])

    def byte_MAKE_CLOSURE(self, argc):
        if PY3:
            # TODO: the py3 docs don't mention this change.
            name = self.pop()
        else:
            name = None
        closure, code = self.popn(2)
        defaults = self.popn(argc)
        globs = self.get_globals_dict()
        fn = self.make_function(None, code, globs, defaults, closure)
        self.push(fn)

    def byte_CALL_FUNCTION(self, arg):
        return self.call_function_from_stack(arg, [], {})

    def byte_CALL_FUNCTION_VAR(self, arg):
        args = self.pop()
        return self.call_function_from_stack(arg, args, {})

    def byte_CALL_FUNCTION_KW(self, arg):
        kwargs = self.pop()
        return self.call_function_from_stack(arg, [], kwargs)

    def byte_CALL_FUNCTION_VAR_KW(self, arg):
        args, kwargs = self.popn(2)
        return self.call_function_from_stack(arg, args, kwargs)

    def call_function_from_stack(self, arg, args, kwargs):
        lenKw, lenPos = divmod(arg, 256)
        namedargs = {}
        for i in range(lenKw):
            key, val = self.popn(2)
            namedargs[key] = val
        namedargs.update(kwargs)
        posargs = self.popn(lenPos)
        posargs.extend(args)
        func = self.pop()
        self.push(self.call_function(func, posargs, namedargs))

    def call_function(self, func, posargs, namedargs=None):
        """Call a VM function with the given arguments and return the result.

        This is were subclass override should occur as well.

        Args:
          func: The function to call.
          posargs: The positional arguments.
          namedargs: The keyword arguments (defaults to {}).
        Returns:
          The return value of the function.
        """
        namedargs = namedargs or {}
        frame = self.frame
        if hasattr(func, 'im_func'):
            # Methods get self as an implicit first parameter.
            if func.im_self:
                posargs.insert(0, func.im_self)
            # The first parameter must be the correct type.
            if not self.isinstance(posargs[0], func.im_class):
                raise TypeError(
                    'unbound method %s() must be called with %s instance '
                    'as first argument (got %s instance instead)' % (
                        func.im_func.func_name,
                        func.im_class.__name__,
                        type(posargs[0]).__name__,
                    )
                )
            func = func.im_func
        return func(*posargs, **namedargs)

    def byte_RETURN_VALUE(self):
        self.return_value = self.pop()
        if self.frame.generator:
            self.frame.generator.finished = True
        return "return"

    def byte_YIELD_VALUE(self):
        self.return_value = self.pop()
        return "yield"

    ## Importing

    def import_name(self, name, fromlist, level):
        """Import the module and return the module object."""
        return __import__(name, self.get_globals_dict(), self.get_locals_dict(),
                          fromlist, level)

    def get_module_attributes(self, mod):
        """Return the modules members as a dict."""
        return {name: getattr(mod, name) for name in dir(mod)}

    def byte_IMPORT_NAME(self, name):
        level, fromlist = self.popn(2)
        frame = self.frame
        self.push(self.import_name(name, fromlist, level))

    def byte_IMPORT_STAR(self):
        # TODO: this doesn't use __all__ properly.
        mod = self.pop()
        attrs = self.get_module_attributes(mod)
        for attr, val in attrs.iteritems():
            if attr[0] != '_':
                self.store_local(attr, val)

    def byte_IMPORT_FROM(self, name):
        mod = self.top()
        attrs = self.get_module_attributes(mod)
        self.push(attrs[name])

    ## And the rest...

    def byte_EXEC_STMT(self):
        stmt, globs, locs = self.popn(3)
        six.exec_(stmt, globs, locs)

    def byte_BUILD_CLASS(self):
        name, bases, methods = self.popn(3)
        self.push(self.make_class(name, bases, methods))

    def byte_LOAD_BUILD_CLASS(self):
        # New in py3
        self.push(__build_class__)

    def byte_STORE_LOCALS(self):
        self.set_locals_dict_bytecode(self.pop())

    if 0:   # Not in py2.7
        def byte_SET_LINENO(self, lineno):
            self.frame.f_lineno = lineno

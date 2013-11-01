"""A pure-Python Python bytecode interpreter."""
# Based on:
# pyvm2 by Paul Swartz (z3p), from http://www.twistedmatrix.com/users/z3p/

from __future__ import print_function, division
import dis
import inspect
import logging
import operator
import sys

import six
from six.moves import reprlib

PY3, PY2 = six.PY3, not six.PY3

from .pyobj import Frame, Block, Method, Object, Function, Class, Generator

log = logging.getLogger(__name__)

if six.PY3:
    byteint = lambda b: b
else:
    byteint = ord

# Create a repr that won't overflow.
repr_obj = reprlib.Repr()
repr_obj.maxother = 120
repr_obj.maxlist = 1000
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
        # The data stack.
        self.stack = []
        self.return_value = None
        self.last_exception = None

    def top(self):
        """Return the value at the top of the stack, with no changes."""
        return self.stack[-1]

    def pop(self, i=0):
        """Pop a value from the stack.

        Default to the top of the stack, but `i` can be a count from the top
        instead.

        """
        return self.stack.pop(-1-i)

    def push(self, *vals):
        """Push values onto the value stack."""
        self.stack.extend(vals)

    def popn(self, n):
        """Pop a number of values from the value stack.

        A list of `n` values is returned, the deepest value first.

        """
        if n:
            ret = self.stack[-n:]
            self.stack[-n:] = []
            return ret
        else:
            return []

    def jump(self, jump):
        """Move the bytecode pointer to `jump`, so it will execute next."""
        self.frame.f_lasti = jump

    def push_block(self, type, handler, level=None):
        if level is None:
            level = len(self.stack)
        self.frame.block_stack.append(Block(type, handler, level))

    def pop_block(self):
        return self.frame.block_stack.pop()

    def pop_block(self):
        return self.frame.block_stack.pop()

    def make_frame(self, code, callargs={}, f_globals=None, f_locals=None):
        log.info("make_frame: code=%r, callargs=%s" % (code, repper(callargs)))
        if f_globals is not None:
            f_globals = f_globals
            if f_locals is None:
                f_locals = f_globals
        elif self.frames:
            f_globals = self.frame.f_globals
            f_locals = {}
        else:
            f_globals = f_locals = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
        f_locals.update(callargs)
        frame = Frame(code, f_globals, f_locals, self.frame)
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

    def resume_frame(self, frame):
        frame.f_back = self.frame
        val = self.run_frame(frame)
        frame.f_back = None
        return val

    def run_code(self, code, f_globals=None, f_locals=None):
        frame = self.make_frame(code, f_globals=f_globals, f_locals=f_locals)
        val = self.run_frame(frame)
        # Check some invariants
        if self.frames:            # pragma: no cover
            raise VirtualMachineError("Frames left over!")
        if self.stack:             # pragma: no cover
            raise VirtualMachineError("Data left on stack! %r" % self.stack)

        return val

    def unwind_block(self, block):
        while len(self.stack) > block.level:
            self.pop()

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        """
        self.push_frame(frame)
        while True:
            opoffset = frame.f_lasti
            byteCode = byteint(frame.f_code.co_code[opoffset])
            frame.f_lasti += 1
            byteName = dis.opname[byteCode]
            arg = None
            arguments = []
            if byteCode >= dis.HAVE_ARGUMENT:
                arg = frame.f_code.co_code[frame.f_lasti:frame.f_lasti+2]
                frame.f_lasti += 2
                intArg = byteint(arg[0]) + (byteint(arg[1])<<8)
                if byteCode in dis.hasconst:
                    arg = frame.f_code.co_consts[intArg]
                elif byteCode in dis.hasfree:
                    if intArg < len(frame.f_code.co_cellvars):
                        arg = frame.f_code.co_cellvars[intArg]
                    else:
                        arg = frame.f_code.co_freevars[intArg-len(frame.f_code.co_cellvars)]
                elif byteCode in dis.hasname:
                    arg = frame.f_code.co_names[intArg]
                elif byteCode in dis.hasjrel:
                    arg = frame.f_lasti + intArg
                elif byteCode in dis.hasjabs:
                    arg = intArg
                elif byteCode in dis.haslocal:
                    arg = frame.f_code.co_varnames[intArg]
                else:
                    arg = intArg
                arguments = [arg]

            if 1:
                op = "%d: %s" % (opoffset, byteName)
                if arguments:
                    op += " %r" % (arguments[0],)
                indent = "    "*(len(self.frames)-1)
                log.info("  %sdata: %s" % (indent, repper(self.stack)))
                log.info("  %sblks: %s" % (indent, repper(self.frame.block_stack)))
                log.info("%s%s" % (indent, op))

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = None

            try:
                if byteName.startswith('UNARY_'):
                    self.unaryOperator(byteName[6:])
                elif byteName.startswith('BINARY_'):
                    self.binaryOperator(byteName[7:])
                elif byteName.startswith('INPLACE_'):
                    self.inplaceOperator(byteName[8:])
                elif PY2 and 'SLICE' in byteName:
                    self.sliceOperator(byteName)
                else:
                    # dispatch
                    bytecode_fn = getattr(self, 'byte_%s' % byteName, None)
                    if not bytecode_fn:            # pragma: no cover
                        raise VirtualMachineError("unknown bytecode type: %s" % byteName)
                    why = bytecode_fn(*arguments)

            except:
                # deal with exceptions encountered while executing the op.
                self.last_exception = sys.exc_info()[:2] + (None,)
                log.exception("Caught exception during execution")
                why = 'exception'

            # Deal with any block management we need to do: fast_block_end

            if why == 'exception':
                #ceval calls PyTraceBack_Here, used for chaining tracebacks between frames
                pass

            if why == 'reraise':
                why = 'exception'

            if why != 'yield':
                while why and frame.block_stack:

                    assert why != 'yield'

                    block = frame.block_stack[-1]
                    if block.type == 'loop' and why == 'continue':
                        self.jump(self.return_value)
                        why = None
                        break

                    self.pop_block()

                    if block.type == 'except-handler':
                       self.unwind_except_handler(block)
                       continue

                    self.unwind_block(block)

                    if block.type == 'loop' and why == 'break':
                        why = None
                        self.jump(block.handler)
                        break

                    if PY2:
                        if (block.type == 'finally' or
                            (block.type == 'setup-except' and why == 'exception') or
                            block.type == 'with'):
                            if why == 'exception':
                                exctype, value, tb = self.last_exception
                                self.push(tb, value, exctype)
                            else:
                                if why in ('return', 'continue'):
                                    self.push(self.return_value)
                                self.push(why)
                            why = None
                            self.jump(block.handler)

                    elif PY3:
                        if (why == 'exception' and 
                            block.type in ['setup-except', 'finally']):

                            self.push_block('except-handler', -1)
                            exctype, value, tb = self.last_exception
                            self.push(tb, value, exctype)
                            # PyErr_Normalize_Exception goes here
                            self.push(tb, value, exctype)
                            why = None
                            self.jump(block.handler)

                        elif block.type == 'finally':
                            if why in ('return', 'continue'):
                                self.push(self.return_value)
                            self.push(why)

                            why = None
                            self.jump(block.handler)
                            break

            if why:
                break

        self.pop_frame()

        if why == 'exception':
            six.reraise(*self.last_exception)

        return self.return_value

    def unwind_except_handler(self, block):
        while len(self.stack) > block.level + 3:
            self.pop()
        exctype = self.pop()
        value = self.pop()
        tb = self.pop()
        self.last_exception = exctype, value, tb

    ## Stack manipulation

    def byte_LOAD_CONST(self, const):
        self.push(const)

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
        frame = self.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.push(val)

    def byte_STORE_NAME(self, name):
        self.frame.f_locals[name] = self.pop()

    def byte_DELETE_NAME(self, name):
        del self.frame.f_locals[name]

    def byte_LOAD_FAST(self, name):
        if name in self.frame.f_locals:
            val = self.frame.f_locals[name]
        else:
            raise UnboundLocalError("local variable '%s' referenced before assignment" % name)
        self.push(val)

    def byte_STORE_FAST(self, name):
        self.frame.f_locals[name] = self.pop()

    def byte_DELETE_FAST(self, name):
        del self.frame.f_locals[name]

    def byte_LOAD_GLOBAL(self, name):
        f = self.frame
        if name in f.f_globals:
            val = f.f_globals[name]
        elif name in f.f_builtins:
            val = f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        self.push(val)

    def byte_LOAD_DEREF(self, name):
        self.push(self.frame.cells[name].get())

    def byte_STORE_DEREF(self, name):
        self.frame.cells[name].set(self.pop())

    def byte_LOAD_LOCALS(self):
        self.push(self.frame.f_locals)

    ## Operators

    UNARY_OPERATORS = {
        'POSITIVE': operator.pos,
        'NEGATIVE': operator.neg,
        'NOT':      operator.not_,
        'CONVERT':  repr,
        'INVERT':   operator.invert,
    }

    def unaryOperator(self, op):
        x = self.pop()
        self.push(self.UNARY_OPERATORS[op](x))

    BINARY_OPERATORS = {
        'POWER':    pow,
        'MULTIPLY': operator.mul,
        'DIVIDE':   getattr(operator, 'div', lambda x,y:None),
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

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x, y))

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
        end = None # we will take this to mean end
        op, count = op[:-2], int(op[-1])
        if count == 1:
            start = self.pop()
        elif count == 2:
            end = self.pop()
        elif count == 3:
            end = self.pop()
            start = self.pop()
        l = self.pop()
        if end == None:
            end = len(l)
        if op.startswith('STORE_'):
            l[start:end] = self.pop()
        elif op.startswith('DELETE_'):
            del l[start:end]
        else:
            self.push(l[start:end])

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
        operator.contains,
        lambda x,y: x not in y,
        lambda x,y: x is y,
        lambda x,y: x is not y,
        lambda x,y: issubclass(x, Exception) and issubclass(x, y)
    ]

    def byte_COMPARE_OP(self, opnum):
        x, y = self.popn(2)
        self.push(self.COMPARE_OPERATORS[opnum](x, y))

    ## Attributes and indexing

    def byte_LOAD_ATTR(self, attr):
        obj = self.pop()
        val = getattr(obj, attr)
        self.push(val)

    def byte_STORE_ATTR(self, name):
        val, obj = self.popn(2)
        setattr(obj, name, val)

    def byte_DELETE_ATTR(self, name):
        obj = self.pop()
        delattr(obj, name)

    def byte_STORE_SUBSCR(self):
        val, obj, subscr = self.popn(3)
        obj[subscr] = val

    def byte_DELETE_SUBSCR(self):
        obj, subscr = self.popn(2)
        del obj[subscr]

    ## Building

    def byte_BUILD_TUPLE(self, count):
        elts = self.popn(count)
        self.push(tuple(elts))

    def byte_BUILD_LIST(self, count):
        elts = self.popn(count)
        self.push(elts)

    def byte_BUILD_MAP(self, size):
        # size is ignored.
        self.push({})

    def byte_STORE_MAP(self):
        the_map, val, key = self.popn(3)
        the_map[key] = val
        self.push(the_map)

    def byte_UNPACK_SEQUENCE(self, count):
        seq = self.pop()
        for x in reversed(seq):
            self.push(x)

    def byte_BUILD_SLICE(self, count):
        # New in Py3
        if count == 2:
            x, y = self.popn(2)
            self.push(slice(x, y))
        elif count == 3:
            x, y, z = self.popn(3)
            self.push(slice(x, y, z))
        else:           # pragma: no cover
            raise VirtualMachineError("Strange BUILD_SLICE count: %r" % count)

    ## Printing

    if 0:   # Only used in the interactive interpreter, not in modules.
        def byte_PRINT_EXPR(self):
            print(self.pop())

    def byte_PRINT_ITEM(self):
        print(self.pop(), end="")

    def byte_PRINT_ITEM_TO(self):
        item = self.pop()
        to = self.top()
        print(item, end="", file=to)

    def byte_PRINT_NEWLINE(self):
        print()

    def byte_PRINT_NEWLINE_TO(self):
        to = self.top()
        print("", file=to)

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

        def byte_JUMP_IF_FALSE(self, jump):
            val = self.top()
            if not val:
                self.jump(jump)

    def byte_POP_JUMP_IF_TRUE(self, jump):
        val = self.pop()
        if val:
            self.jump(jump)

    def byte_POP_JUMP_IF_FALSE(self, jump):
        val = self.pop()
        if not val:
            self.jump(jump)

    def byte_JUMP_IF_TRUE_OR_POP(self, jump):
        val = self.top()
        if val:
            self.jump(jump)
        else:
            self.pop()

    def byte_JUMP_IF_FALSE_OR_POP(self, jump):
        val = self.top()
        if not val:
            self.jump(jump)
        else:
            self.pop()

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
        status = self.pop()
        if isinstance(status, str):
            why = status
            if why in ('return', 'continue'):
                self.return_value = self.pop()
            if why == 'silenced': # PY3
                block = self.pop_block()
                assert block.type == 'except-handler'
                self.unwind_except_handler(block)
                why = None
        elif status is None:
            why = None
        elif issubclass(status, BaseException):
            exctype = status
            val = self.pop()
            tb = self.pop()
            self.last_exception = (exctype, val, tb)
            why = 'reraise'
        else:       # pragma: no cover
            raise VirtualMachineError("Confused END_FINALLY")
        return why

    def byte_POP_BLOCK(self):
        self.pop_block()

    def byte_RAISE_VARARGS(self, argc):
        if PY3:
            return self.byte_RAISE_VARARGS_py3(argc)

        # NOTE: the dis docs are completely wrong about the order of the
        # operands on the stack!
        exctype = val = tb = None

        if argc == 0: # reraise
            exctype, val, tb = self.last_exception
        elif argc == 1:
            # `raise Exception`
            exctype = self.pop()
        elif argc == 2:
            # `raise Exception("instance")` or 
            # `raise Exception, Value
            val = self.pop()
            exctype = self.pop()
        elif argc == 3:
            # `raise Exception, Value, traceback`
            tb = self.pop()
            val = self.pop()
            exctype = self.pop()

        # There are a number of forms of "raise", normalize them somewhat.
        if isinstance(exctype, BaseException):
            val = exctype
            exctype = type(val)
        elif val is None: # still needed?
            val = exctype()

        self.last_exception = (exctype, val, tb)

        return 'exception' #TODO: test coverage hole on reraise in PY2

    def byte_RAISE_VARARGS_py3(self, argc):
        cause = exc = None
        if argc == 2:
            cause = self.pop()
            exc = self.pop()
        elif argc == 1:
            exc = self.pop()

        return self.do_raise(exc, cause)

    def do_raise(self, exc, cause):
        """ A py3-like do_raise"""
        if exc == None: # reraise
            exc_type, val, tb = self.last_exception
            if exc_type == None:
                return 'exception'
                # raise Exception("No active exception to reraise")
            return 'reraise'
        elif type(exc) == type: # as in `raise ValueError`
            exc_type = exc
            val = exc() # make an instance
        elif isinstance(exc, BaseException): # as in `raise ValueError('foo')
            exc_type = type(exc)
            val = exc
        else:
            return 'exception'
            # raise TypeError("exceptions must derive from BaseException")

        # if you reach this point, you're guaranteed that
        # val is a valid exception instance and exc_type is its class
        if cause:
            if type(cause) == type:
                cause = cause()
            elif not isinstance(cause, BaseException):
                return 'exception'
                # raise Exception("Exception causes must derive from BaseException")

            val.__cause__ = cause

        self.last_exception = exc_type, val, val.__traceback__
        return 'exception'

    def byte_POP_EXCEPT(self):
        block = self.pop_block()
        if PY2:
            if block.type != 'setup-except':
                raise Exception("popped block is not an except handler")
        if PY3:
            if block.type != 'except-handler':
                raise Exception("popped block is not an except handler")
        self.unwind_except_handler(block)

    def byte_SETUP_WITH(self, dest):
        ctxmgr = self.pop()
        self.push(ctxmgr.__exit__)
        ctxmgr_obj = ctxmgr.__enter__()
        if PY2:
            self.push_block('with', dest)
        if PY3:
            self.push_block('finally', dest)
        self.push(ctxmgr_obj)

    def byte_WITH_CLEANUP(self):
        # The code here does some weird stack manipulation: the exit function
        # is buried in the stack, and where depends on what's on top of it.
        # Pull out the exit function, and leave the rest in place.
        v = w = None
        u = self.top()
        if u is None: # same in 2/3
            exit_func = self.pop(1)
        elif isinstance(u, str): # same in 2/3
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
            if PY3:
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
            # An error occurred, and was suppressed, pop it from the stack.
            if PY2:
                self.popn(3)
                self.push(None)
            if PY3:
                self.push('silenced')

    ## Functions

    def byte_MAKE_FUNCTION(self, argc):
        if PY3:
            name = self.pop()
        else:
            name = None
        code = self.pop()
        defaults = self.popn(argc)
        globs = self.frame.f_globals
        fn = Function(name, code, globs, defaults, None, self)
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
        globs = self.frame.f_globals
        fn = Function(None, code, globs, defaults, closure, self)
        self.push(fn)

    def byte_CALL_FUNCTION(self, arg):
        return self.call_function(arg, [], {})

    def byte_CALL_FUNCTION_VAR(self, arg):
        args = self.pop()
        return self.call_function(arg, args, {})

    def byte_CALL_FUNCTION_KW(self, arg):
        kwargs = self.pop()
        return self.call_function(arg, [], kwargs)

    def byte_CALL_FUNCTION_VAR_KW(self, arg):
        args, kwargs = self.popn(2)
        return self.call_function(arg, args, kwargs)

    def call_function(self, arg, args, kwargs):
        lenKw, lenPos = divmod(arg, 256)
        namedargs = {}
        for i in range(lenKw):
            key, val = self.popn(2)
            namedargs[key] = val
        namedargs.update(kwargs)
        posargs = self.popn(lenPos)
        posargs.extend(args)

        func = self.pop()
        frame = self.frame
        if hasattr(func, 'im_func'):
            # Methods get self as an implicit first parameter.
            if func.im_self:
                posargs.insert(0, func.im_self)
            # The first parameter must be the correct type.
            if 0:   # TODO: do we need to do this check?
                if not isinstance(posargs[0], func.im_class):
                    raise TypeError(
                        'unbound method %s() must be called with %s instance as first argument (got %s instance instead)' %
                        (func.im_func.func_name, func.im_class.__name__, type(posargs[0]).__name__)
                    )
            func = func.im_func
        retval = func(*posargs, **namedargs)
        self.push(retval)

    def byte_RETURN_VALUE(self):
        self.return_value = self.pop()
        if self.frame.generator:
            self.frame.generator.finished = True
        return "return"

    def byte_YIELD_VALUE(self):
        self.return_value = self.pop()
        return "yield"

    ## Importing

    def byte_IMPORT_NAME(self, name):
        level, fromlist = self.popn(2)
        frame = self.frame
        self.push(__import__(name, frame.f_globals, frame.f_locals, fromlist, level))

    def byte_IMPORT_STAR(self):
        # TODO: this doesn't use __all__ properly.
        mod = self.pop()
        for attr in dir(mod):
            if attr[0] != '_':
                self.frame.f_locals[attr] = getattr(mod, attr)

    def byte_IMPORT_FROM(self, name):
        mod = self.top()
        self.push(getattr(mod, name))

    ## And the rest...

    def byte_EXEC_STMT(self):
        stmt, globs, locs = self.popn(3)
        six.exec_(stmt, globs, locs)

    def byte_BUILD_CLASS(self):
        name, bases, methods = self.popn(3)
        self.push(Class(name, bases, methods))

    def byte_LOAD_BUILD_CLASS(self):
        # New in py3
        self.push(__build_class__)

    def byte_STORE_LOCALS(self):
        self.frame.f_locals = self.pop()

    if 0:   # Not in py2.7
        def byte_SET_LINENO(self, lineno):
            self.frame.f_lineno = lineno

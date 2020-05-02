"""A pure-Python Python bytecode interpreter."""
# Based on:
# pyvm2 by Paul Swartz (z3p), from http://www.twistedmatrix.com/users/z3p/

from __future__ import print_function, division
import linecache
import logging
import operator
import sys

import six
from six.moves import reprlib

from xdis import PYTHON3, PYTHON_VERSION
from xdis.op_imports import get_opcode_module

from xpython.pyobj import Frame, Block, Function, Generator

PY2 = not PYTHON3
log = logging.getLogger(__name__)

if PYTHON3:
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
    def __init__(self, python_version=PYTHON_VERSION):
        # The call stack of frames.
        self.frames = []
        # The current frame.
        self.frame = None
        self.return_value = None
        self.last_exception = None
        self.last_traceback_limit = None
        self.version = python_version

        # This is somewhat hoaky:
        # Give byteop routines a way to raise an error, without having
        # to import this file. We import from from byteops.
        # Alternatively, VirtualMachineError could be
        # pulled out of this file
        self.VirtualMachineError = VirtualMachineError

        int_vers = int(python_version * 10)
        version_info = (int_vers // 10, int_vers % 10)
        self.opc = get_opcode_module(version_info)
        if int_vers < 30:
            if int_vers == 27:
                from xpython.byteop.byteop27 import ByteOp27
                self.byteop = ByteOp27(self)
            elif int_vers == 26:
                from xpython.byteop.byteop26 import ByteOp26
                self.byteop = ByteOp26(self)
                pass
            elif int_vers == 25:
                from xpython.byteop.byteop25 import ByteOp25
                self.byteop = ByteOp25(self)
                pass
            else:
                raise RuntimeError("Version %s not supported yet" % python_version)
            pass
        else:
            # 3.0 or greater
            if int_vers >= 34:
                if int_vers == 34:
                    from xpython.byteop.byteop34 import ByteOp34
                    self.byteop = ByteOp34(self)
                elif int_vers == 35:
                    from xpython.byteop.byteop35 import ByteOp35
                    self.byteop = ByteOp35(self)
                    pass
                else:
                    raise RuntimeError("Version %s not supported yet" % python_version)
                pass
            else:
                if int_vers == 32:
                    from xpython.byteop.byteop32 import ByteOp32
                    self.byteop = ByteOp32(self)
                elif int_vers == 33:
                    from xpython.byteop.byteop33 import ByteOp33
                    self.byteop = ByteOp33(self)
                else:
                    raise RuntimeError("Version %s not supported yet" % python_version)


    def top(self):
        """Return the value at the top of the stack, with no changes."""
        return self.frame.stack[-1]

    def pop(self, i=0):
        """Pop a value from the stack.

        Default to the top of the stack, but `i` can be a count from the top
        instead.

        """
        return self.frame.stack.pop(-1 - i)

    def push(self, *vals):
        """Push values onto the value stack."""
        self.frame.stack.extend(vals)

    def popn(self, n):
        """Pop a number of values from the value stack.

        A list of `n` values is returned, the deepest value first.

        """
        if n:
            ret = self.frame.stack[-n:]
            self.frame.stack[-n:] = []
            return ret
        else:
            return []

    def peek(self, n):
        """Get a value `n` entries down in the stack, without changing the stack."""
        return self.frame.stack[-n]

    def jump(self, jump):
        """Move the bytecode pointer to `jump`, so it will execute next."""
        self.frame.f_lasti = jump

    def push_block(self, type, handler=None, level=None):
        if level is None:
            level = len(self.frame.stack)
        self.frame.block_stack.append(Block(type, handler, level))

    def pop_block(self):
        return self.frame.block_stack.pop()

    def make_frame(self, code, callargs={}, f_globals=None, f_locals=None):
        log.debug("make_frame: code=%r, callargs=%s" % (code, repper(callargs)))
        if f_globals is not None:
            f_globals = f_globals
            if f_locals is None:
                f_locals = f_globals
        elif self.frames:
            f_globals = self.frame.f_globals
            f_locals = {}
        else:
            f_globals = f_locals = {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "__package__": None,
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

    def print_frames(self):
        """Print the call stack, for debugging."""
        for f in self.frames:
            filename = f.f_code.co_filename
            lineno = f.line_number()
            print('  File "%s", line %d, in %s' % (filename, lineno, f.f_code.co_name))
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            if line:
                print("    " + line.strip())

    def resume_frame(self, frame):
        frame.f_back = self.frame
        val = self.run_frame(frame)
        frame.f_back = None
        return val

    def run_code(self, code, f_globals=None, f_locals=None):
        frame = self.make_frame(code, f_globals=f_globals, f_locals=f_locals)
        val = self.run_frame(frame)
        # Check some invariants
        if self.frames:  # pragma: no cover
            raise VirtualMachineError("Frames left over!")
        if self.frame and self.frame.stack:  # pragma: no cover
            raise VirtualMachineError("Data left on stack! %r" % self.frame.stack)

        return val

    def unwind_block(self, block):
        if block.type == "except-handler":
            offset = 3
        else:
            offset = 0

        while len(self.frame.stack) > block.level + offset:
            self.pop()

        if block.type == "except-handler":
            tb, value, exctype = self.popn(3)
            self.last_exception = exctype, value, tb

    def parse_byte_and_args(self):
        """ Parse 1 - 3 bytes of bytecode into
        an instruction and optionally arguments."""
        f = self.frame
        opoffset = f.f_lasti
        line_number = self.linestarts.get(opoffset, None)
        f_code = f.f_code
        co_code = f_code.co_code
        byteCode = byteint(co_code[opoffset])
        f.f_lasti += 1
        byteName = self.opc.opname[byteCode]
        arg = None
        arguments = []
        if byteCode >= self.opc.HAVE_ARGUMENT:
            arg = co_code[f.f_lasti : f.f_lasti + 2]
            f.f_lasti += 2
            intArg = byteint(arg[0]) + (byteint(arg[1]) << 8)
            if byteCode in self.opc.CONST_OPS:
                arg = f_code.co_consts[intArg]
            elif byteCode in self.opc.FREE_OPS:
                if intArg < len(f_code.co_cellvars):
                    arg = f_code.co_cellvars[intArg]
                else:
                    var_idx = intArg - len(f.f_code.co_cellvars)
                    arg = f_code.co_freevars[var_idx]
            elif byteCode in self.opc.NAME_OPS:
                arg = f_code.co_names[intArg]
            elif byteCode in self.opc.JREL_OPS:
                arg = f.f_lasti + intArg
            elif byteCode in self.opc.JABS_OPS:
                arg = intArg
            elif byteCode in self.opc.LOCAL_OPS:
                arg = f_code.co_varnames[intArg]
            else:
                arg = intArg
            arguments = [arg]

        return byteName, arguments, opoffset, line_number

    def log(self, byteName, arguments, opoffset, line_number):
        """ Log arguments, block stack, and data stack for each opcode."""
        if line_number is not None:
            op = "Line %4d, " % line_number
        else:
            op = " " * 11

        op += "%3d: %s" % (opoffset, byteName)
        if arguments:
            op += " %r" % (arguments[0],)
        indent = "    " * (len(self.frames) - 1)
        stack_rep = repper(self.frame.stack)
        block_stack_rep = repper(self.frame.block_stack)

        log.debug("  %sdata: %s" % (indent, stack_rep))
        log.debug("  %sblks: %s" % (indent, block_stack_rep))
        log.info("%s%s" % (indent, op))

    def dispatch(self, byteName, arguments, opoffset):
        """ Dispatch by bytename to the corresponding methods.
        Exceptions are caught and set on the virtual machine."""

        def instruction_info():
            frame = self.frame
            code = frame.f_code
            return ("%d: %s %s\n\t%s in %s:%s" %
                    (opoffset, byteName, arguments,
                     code.co_name, code.co_filename, frame.f_lineno))

        why = None
        try:
            if byteName.startswith("UNARY_"):
                self.unaryOperator(byteName[6:])
            elif byteName.startswith("BINARY_"):
                self.binaryOperator(byteName[7:])
            elif byteName.startswith("INPLACE_"):
                self.inplaceOperator(byteName[8:])
            elif "SLICE+" in byteName:
                self.sliceOperator(byteName)
            else:
                # dispatch
                if hasattr(self.byteop, byteName):
                    bytecode_fn = getattr(self.byteop, byteName, None)
                else:
                    # This branch is disappearing...
                    bytecode_fn = getattr(self, "byte_%s" % byteName, None)

                if not bytecode_fn:  # pragma: no cover
                    raise VirtualMachineError("Unknown bytecode type: %s\n\t%s" %
                                              (instruction_info(), byteName))
                why = bytecode_fn(*arguments)

        except:
            # Deal with exceptions encountered while executing the op.
            # In Python 2.x we are not capturing the traceback as seen by
            # the interpreter. In Python 3.x we are. We may want to do something
            # fancier in Python 2.x.
            # In both cases there is a *lot* of interpreter junk at the end which
            # should be removed.
            self.last_exception = sys.exc_info()
            log.info(
                ("Caught exception during execution of "
                 "instruction:\n\t%s" % instruction_info())
            )
            why = "exception"

        return why

    def manage_block_stack(self, why):
        """ Manage a frame's block stack.
        Manipulate the block stack and data stack for looping,
        exception handling, or returning."""
        assert why != "yield"

        block = self.frame.block_stack[-1]
        if block.type == "loop" and why == "continue":
            self.jump(self.return_value)
            why = None
            return why

        self.pop_block()
        self.unwind_block(block)

        if block.type == "loop" and why == "break":
            why = None
            self.jump(block.handler)
            return why

        if PY2:
            if (
                block.type == "finally"
                or (block.type == "setup-except" and why == "exception")
                or block.type == "with"
            ):
                if why == "exception":
                    exctype, value, tb = self.last_exception
                    self.push(tb, value, exctype)
                else:
                    if why in ("return", "continue"):
                        self.push(self.return_value)
                    self.push(why)

                why = None
                self.jump(block.handler)
                return why

        elif PYTHON3:
            if why == "exception" and block.type in ["setup-except", "finally"]:
                self.push_block("except-handler")
                exctype, value, tb = self.last_exception
                self.push(tb, value, exctype)
                # PyErr_Normalize_Exception goes here
                self.push(tb, value, exctype)
                why = None
                self.jump(block.handler)
                return why

            elif block.type == "finally":
                if why in ("return", "continue"):
                    self.push(self.return_value)
                self.push(why)

                why = None
                self.jump(block.handler)
                return why

        return why

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        """
        self.push_frame(frame)
        self.f_code = self.frame.f_code
        self.linestarts = dict(self.opc.findlinestarts(self.f_code, dup_lines=True))

        opoffset = 0
        while True:
            byteName, arguments, opoffset, line_number = self.parse_byte_and_args()
            if log.isEnabledFor(logging.INFO):
                self.log(byteName, arguments, opoffset, line_number)

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = self.dispatch(byteName, arguments, opoffset)
            if why == "exception":
                # TODO: ceval calls PyTraceBack_Here, not sure what that does.
                # FIXME: fakeup a traceback from where we are
                pass

            if why == "reraise":
                why = "exception"

            if why != "yield":
                while why and frame.block_stack:
                    # Deal with any block management we need to do.
                    why = self.manage_block_stack(why)

            if why:
                break

        # TODO: handle generator exception state

        self.pop_frame()

        if why == "exception":
            if self.last_exception:
                six.reraise(*self.last_exception)
            else:
                raise VirtualMachineError("Borked exception recording")
            # if self.exception and .... ?
            # log.error("Haven't finished traceback handling, nulling traceback information for now")
            # six.reraise(self.last_exception[0], None)

        return self.return_value

    ## Names

    def byte_STORE_NAME(self, name):
        self.frame.f_locals[name] = self.pop()

    def byte_DELETE_NAME(self, name):
        del self.frame.f_locals[name]

    def byte_STORE_GLOBAL(self, name):
        f = self.frame
        f.f_globals[name] = self.pop()

    def byte_LOAD_LOCALS(self):
        self.push(self.frame.f_locals)

    ## Operators

    UNARY_OPERATORS = {
        "POSITIVE": operator.pos,
        "NEGATIVE": operator.neg,
        "NOT": operator.not_,
        "CONVERT": repr,
        "INVERT": operator.invert,
    }

    def unaryOperator(self, op):
        x = self.pop()
        self.push(self.UNARY_OPERATORS[op](x))

    BINARY_OPERATORS = {
        "POWER": pow,
        "MULTIPLY": operator.mul,
        "DIVIDE": getattr(operator, "div", lambda x, y: None),
        "FLOOR_DIVIDE": operator.floordiv,
        "TRUE_DIVIDE": operator.truediv,
        "MODULO": operator.mod,
        "ADD": operator.add,
        "SUBTRACT": operator.sub,
        "SUBSCR": operator.getitem,
        "LSHIFT": operator.lshift,
        "RSHIFT": operator.rshift,
        "AND": operator.and_,
        "XOR": operator.xor,
        "OR": operator.or_,
    }

    if PYTHON_VERSION >= 3.5:
        BINARY_OPERATORS["MATRIX_MULTIPLY"] = operator.matmul

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x, y))

    def inplaceOperator(self, op):
        x, y = self.popn(2)
        if op == "POWER":
            x **= y
        elif op == "MULTIPLY":
            x *= y
        elif op in ["DIVIDE", "FLOOR_DIVIDE"]:
            x //= y
        elif op == "TRUE_DIVIDE":
            x /= y
        elif op == "MODULO":
            x %= y
        elif op == "ADD":
            x += y
        elif op == "SUBTRACT":
            x -= y
        elif op == "LSHIFT":
            x <<= y
        elif op == "RSHIFT":
            x >>= y
        elif op == "AND":
            x &= y
        elif op == "XOR":
            x ^= y
        elif op == "OR":
            x |= y
        # 3.5 on
        elif op == "MATRIX_MULTIPLY":
            operator.imatmul(x, y)
        else:  # pragma: no cover
            raise VirtualMachineError("Unknown in-place operator: %r" % op)
        self.push(x)

    def sliceOperator(self, op):
        start = 0
        end = None  # we will take this to mean end
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
        if op.startswith("STORE_"):
            l[start:end] = self.pop()
        elif op.startswith("DELETE_"):
            del l[start:end]
        else:
            self.push(l[start:end])

    ## Attributes and indexing

    def byte_STORE_ATTR(self, name):
        val, obj = self.popn(2)
        setattr(obj, name, val)

    def byte_DELETE_ATTR(self, name):
        obj = self.pop()
        delattr(obj, name)

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
        else:  # pragma: no cover
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

    ## Blocks

    def byte_BREAK_LOOP(self):
        return "break"

    def byte_CONTINUE_LOOP(self, dest):
        # This is a trick with the return value.
        # While unrolling blocks, continue and return both have to preserve
        # state as the finally blocks are executed.  For continue, it's
        # where to jump to, for return, it's the value to return.  It gets
        # pushed on the stack for both, so continue puts the jump destination
        # into return_value.
        self.return_value = dest
        return "continue"

    def byte_END_FINALLY(self):
        """
        Terminates a "finally" clause. The interpreter recalls whether the
        exception has to be re-raised, or whether the function
        returns, and continues with the outer-next block.
        """
        v = self.pop()
        if isinstance(v, str):
            why = v
            if why in ("return", "continue"):
                self.return_value = self.pop()
            if why == "silenced":  # PYTHON3
                block = self.pop_block()
                assert block.type == "except-handler"
                self.unwind_block(block)
                why = None
        elif v is None:
            why = None
        elif issubclass(v, BaseException):
            exctype = v
            val = self.pop()
            tb = self.pop()
            self.last_exception = (exctype, val, tb)
            why = "reraise"
        else:  # pragma: no cover
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
                return "reraise"
            else:
                return "exception"

    elif PYTHON3:

        def byte_RAISE_VARARGS(self, argc):
            cause = exc = None
            if argc == 2:
                cause = self.pop()
                exc = self.pop()
            elif argc == 1:
                exc = self.pop()
            return self.do_raise(exc, cause)

        def do_raise(self, exc, cause):
            if exc is None:  # reraise
                exc_type, val, tb = self.last_exception
                if exc_type is None:
                    return "exception"  # error
                else:
                    return "reraise"

            elif type(exc) == type:
                # As in `raise ValueError`
                exc_type = exc
                val = exc()  # Make an instance.
            elif isinstance(exc, BaseException):
                # As in `raise ValueError('foo')`
                exc_type = type(exc)
                val = exc
            else:
                return "exception"  # error

            # If you reach this point, you're guaranteed that
            # val is a valid exception instance and exc_type is its class.
            # Now do a similar thing for the cause, if present.
            if cause:
                if type(cause) == type:
                    cause = cause()
                elif not isinstance(cause, BaseException):
                    return "exception"  # error

                val.__cause__ = cause

            self.last_exception = exc_type, val, val.__traceback__
            return "exception"

    def byte_POP_EXCEPT(self):
        block = self.pop_block()
        if block.type != "except-handler":
            raise Exception("popped block is not an except handler")
        self.unwind_block(block)

    def byte_SETUP_WITH(self, dest):
        ctxmgr = self.pop()
        self.push(ctxmgr.__exit__)
        ctxmgr_obj = ctxmgr.__enter__()
        if PY2:
            self.push_block("with", dest)
        elif PYTHON3:
            self.push_block("finally", dest)
        self.push(ctxmgr_obj)

    ## Functions

    def byte_MAKE_CLOSURE(self, argc):
        if PYTHON3:
            # TODO: the py3 docs don't mention this change.
            name = self.pop()
        else:
            name = None
        closure, code = self.popn(2)
        defaults = self.popn(argc)
        globs = self.frame.f_globals
        fn = Function(name, code, globs, defaults, closure, self)
        self.push(fn)

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
        namedargs = {}
        if self.version < 3.6:
            lenKw, lenPos = divmod(arg, 256)
            for i in range(lenKw):
                key, val = self.popn(2)
                namedargs[key] = val
            namedargs.update(kwargs)
        else:
            lenKw, lenPos = 0, arg
        posargs = self.popn(lenPos)
        posargs.extend(args)

        func = self.pop()
        if hasattr(func, "im_func"):
            # Methods get self as an implicit first parameter.
            if func.im_self:
                posargs.insert(0, func.im_self)
            # The first parameter must be the correct type.
            if not isinstance(posargs[0], func.im_class):
                raise TypeError(
                    "unbound method %s() must be called with %s instance "
                    "as first argument (got %s instance instead)"
                    % (
                        func.im_func.func_name,
                        func.im_class.__name__,
                        type(posargs[0]).__name__,
                    )
                )
            func = func.im_func

        # FIXME: there has to be a better way to do this, like on
        # initial loading of the code rather than every function call.
        if not hasattr(func, "version"):
            try:
                func.version = self.version
            except:
                # Could be a builtin type, or "str", etc.
                pass

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

    def byte_YIELD_FROM(self):
        u = self.pop()
        x = self.top()

        try:
            if not isinstance(x, Generator) or u is None:
                # Call next on iterators.
                retval = next(x)
            else:
                retval = x.send(u)
            self.return_value = retval
        except StopIteration as e:
            self.pop()
            self.push(e.value)
        else:
            # YIELD_FROM decrements f_lasti, so that it will be called
            # repeatedly until a StopIteration is raised.
            self.jump(self.frame.f_lasti - 1)
            # Returning "yield" prevents the block stack cleanup code
            # from executing, suspending the frame in its current state.
            return "yield"

    ## Importing

    ## And the rest...

    if 0:  # Not in py2.7

        def byte_SET_LINENO(self, lineno):
            self.frame.f_lineno = lineno

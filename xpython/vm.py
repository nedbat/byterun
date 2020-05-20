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

from xdis import (
    code2num,
    CO_NEWLOCALS,
    PYTHON3,
    PYTHON_VERSION,
    IS_PYPY,
    op_has_argument,
    next_offset,
)
from xdis.op_imports import get_opcode_module

from xpython.pyobj import Frame, Block, traceback_from_frame
from xpython.byteop import get_byteop

PY2 = not PYTHON3
log = logging.getLogger(__name__)

if PYTHON3:
    byteint = lambda b: b
else:
    byteint = ord

LINE_NUMBER_WIDTH = 4
LINE_NUMBER_WIDTH_FMT = "L. %%-%dd@" % LINE_NUMBER_WIDTH
LINE_NUMBER_SPACES = " " * (LINE_NUMBER_WIDTH + len("L. ")) + "@"

# Create a repr that won't overflow.
repr_obj = reprlib.Repr()
repr_obj.maxother = 120
repper = repr_obj.repr


class PyVMError(Exception):
    """For raising errors in the operation of the VM."""

    pass


class PyVMRuntimeError(Exception):
    """RuntimeError in operation of PyVM."""

    pass


class PyVMUncaughtException(Exception):
    """Uncaught RuntimeError in operation of PyVM."""

    pass


def format_instruction(
    frame, opc, byteName, intArg, arguments, opoffset, line_number, extra_debug
):
    code = frame.f_code if frame else None
    byteCode = opc.opmap.get(byteName, 0)
    if hasattr(opc, "opcode_arg_fmt") and byteName in opc.opcode_arg_fmt:
        argrepr = opc.opcode_arg_fmt[byteName](intArg)
    elif intArg is None:
        argrepr = ""
    elif byteCode in opc.COMPARE_OPS:
        argrepr = opc.cmp_op[intArg]
    elif isinstance(arguments, list) and arguments:
        argrepr = arguments[0]
    else:
        argrepr = arguments

    line_str = (
        LINE_NUMBER_SPACES
        if line_number is None
        else LINE_NUMBER_WIDTH_FMT % line_number
    )
    mess = "%s%3d: %s %s" % (line_str, opoffset, byteName, argrepr)
    if extra_debug and frame:
        mess += " %s in %s:%s" % (code.co_name, code.co_filename, frame.f_lineno)
    return mess


class PyVM(object):
    def __init__(
        self,
        python_version=PYTHON_VERSION,
        is_pypy=IS_PYPY,
        vmtest_testing=False,
        format_instruction_func=format_instruction,
    ):
        # The call stack of frames.
        self.frames = []
        # The current frame.
        self.frame = None
        self.return_value = None
        self.last_exception = None
        self.last_traceback_limit = None
        self.last_traceback = None
        self.version = python_version
        self.is_pypy = is_pypy
        self.format_instruction = format_instruction_func

        # FIXME: until we figure out how to fix up test/vmtest.el
        # This changes how we report a VMRuntime error.
        self.vmtest_testing = vmtest_testing

        # Like sys.exc_info() tuple
        self.last_exception = None

        # Sometimes we need a native function (e.g. for method lookup), but
        # most of the time we want a VM function defined in pyobj.
        # This maps between the two.
        self.fn2native = {}

        self.in_exception_processing = False

        # This is somewhat hoaky:
        # Give byteop routines a way to raise an error, without having
        # to import this file. We import from from byteops.
        # Alternatively, VMError could be
        # pulled out of this file
        self.PyVMError = PyVMError

        int_vers = int(python_version * 10)
        version_info = (int_vers // 10, int_vers % 10)
        variant = "pypy" if is_pypy else None
        self.opc = get_opcode_module(version_info, variant)
        self.byteop = get_byteop(self, python_version, is_pypy)

    ##############################################
    # Frame operations. First the frame stack....
    ##############################################
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

    # end of frame stack operations
    # onto frame block operations..

    def push_block(self, type, handler=None, level=None):
        if level is None:
            level = len(self.frame.stack)
        self.frame.block_stack.append(Block(type, handler, level))

    def pop_block(self):
        return self.frame.block_stack.pop()

    def top_block(self):
        return self.frame.block_stack[-1]

    def jump(self, jump):
        """Move the bytecode pointer to `jump`, so it will execute next,
        However we subtract one from the offset, because fetching the
        next instruction adds one before fetching.
        """
        # The previous pyvm2.py code *always* had self.frame.f_lasti
        # represent the *next* instruction rather than the *last* or
        # current instruction currently under execution. While this
        # was easier to code, consisitent and worked, IT DID NOT
        # REPRESENT PYTHON's semantics. It became unbearable when I
        # added a debugger for x-python that relies on
        # self.frame.f_last_i being correct.
        self.frame.f_lasti = jump
        self.frame.fallthrough = False

    def make_frame(self, code, callargs={}, f_globals=None, f_locals=None):
        # The callargs default is safe because we never modify the dict.
        # pylint: disable=dangerous-default-value
        log.debug(
            "make_frame: code=%r, callargs=%s, f_globals=%r, f_locals=%r",
            code,
            repper(callargs),
            (type(f_globals), id(f_globals)),
            (type(f_locals), id(f_locals)),
        )
        if f_globals is not None:
            f_globals = f_globals
            if f_locals is None:
                f_locals = f_globals
        elif self.frames:
            f_globals = self.frame.f_globals
            if f_locals is None:
                f_locals = {}
        else:
            # TODO(ampere): __name__, __doc__, __package__ below are not correct
            f_globals = f_locals = {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "__package__": None,
            }

        # Implement NEWLOCALS flag. See Objects/frameobject.c in CPython.
        if code.co_flags & CO_NEWLOCALS:
            f_locals = {"__locals__": {}}

        f_locals.update(callargs)
        frame = Frame(code, f_globals, f_locals, self.frame, version=self.version)
        log.debug("%r", frame)
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
        """Print the call stack for debugging. Note that the
        format exactly the same as in traceback.print_tb()
        """
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
        log.debug("resume_frame: %r", frame)

        # Make sure we advance to the next instruction after where we left off.
        if frame.f_lasti == -1:
            # We are just starting out. Set offset to the first
            # instruction, and signal that we should not increment
            # this before fetching next instruction.
            frame.fallthrough = False
            frame.f_lasti = 0
        else:
            frame.fallthrough = True

        val = self.run_frame(frame)
        frame.f_back = None
        return val

    ##############################################
    # End Frame operations.
    ##############################################

    # This is the main entry point
    def run_code(self, code, f_globals=None, f_locals=None):
        """run code using f_globals and f_locals in our VM"""
        frame = self.make_frame(code, f_globals=f_globals, f_locals=f_locals)
        try:
            val = self.run_frame(frame)
        except Exception:
            # Until we get test/vmtest.py under control:
            if self.vmtest_testing:
                raise
            if self.last_traceback:
                self.last_traceback.print_tb()
                print("%s" % self.last_exception[0].__name__, end="")
                tail = (
                    (": %s" % "\n".join(self.last_exception[1].args))
                    if self.last_exception[1].args
                    else ""
                )
                print(tail)
            raise PyVMUncaughtException

        # Frame ran to normal completion... check some invariants
        if self.frames:  # pragma: no cover
            raise PyVMError("Frames left over!")
        if self.frame and self.frame.stack:  # pragma: no cover
            raise PyVMError("Data left on stack! %r" % self.frame.stack)

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

    def parse_byte_and_args(self, byteCode):

        """ Parse 1 - 3 bytes of bytecode into
        an instruction and optionally arguments."""

        f = self.frame
        f_code = f.f_code
        co_code = f_code.co_code
        extended_arg = 0

        # Note: There is never more than one argument.
        # The list size is used to indicate whether an argument
        # exists or not.
        # FIMXE: remove and use intArg as a indicator of whether
        # the argument exists.
        arguments = []
        intArg = None

        while True:
            if f.fallthrough:
                f.f_lasti = next_offset(byteCode, self.opc, f.f_lasti)
            else:
                # Jump instructions must set this False.
                f.fallthrough = True
            opoffset = f.f_lasti
            line_number = self.frame.linestarts.get(opoffset, None)
            if line_number is not None:
                f.f_lineno = line_number
            byteCode = byteint(co_code[opoffset])
            byteName = self.opc.opname[byteCode]
            arg_offset = opoffset + 1
            arg = None

            if op_has_argument(byteCode, self.opc):
                if PYTHON_VERSION >= 3.6:
                    intArg = code2num(co_code, arg_offset) | extended_arg
                    # Note: Python 3.6.0a1 is 2, for 3.6.a3 and beyond we have 1
                    arg_offset += 1
                    if byteCode == self.opc.EXTENDED_ARG:
                        extended_arg = intArg << 8
                        continue
                    else:
                        extended_arg = 0
                else:
                    intArg = (
                        code2num(co_code, arg_offset)
                        + code2num(co_code, arg_offset + 1) * 256
                        + extended_arg
                    )
                    arg_offset += 2
                    if byteCode == self.opc.EXTENDED_ARG:
                        extended_arg = intArg * 65536
                        continue
                    else:
                        extended_arg = 0

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
                    # Many relative jumps are conditional,
                    # so setting f.fallthrough is wrong.
                    arg = arg_offset + intArg
                elif byteCode in self.opc.JABS_OPS:
                    # We probably could set fallthough, since many (all?)
                    # of these are unconditional, but we'll make the jump do
                    # the work of setting.
                    arg = intArg
                elif byteCode in self.opc.LOCAL_OPS:
                    arg = f_code.co_varnames[intArg]
                else:
                    arg = intArg
                arguments = [arg]
            break

        return byteName, byteCode, intArg, arguments, opoffset, line_number

    def log(self, byteName, intArg, arguments, opoffset, line_number):
        """ Log arguments, block stack, and data stack for each opcode."""
        op = self.format_instruction(
            self.frame,
            self.opc,
            byteName,
            intArg,
            arguments,
            opoffset,
            line_number,
            log.isEnabledFor(logging.DEBUG),
        )
        indent = "    " * (len(self.frames) - 1)
        stack_rep = repper(self.frame.stack)
        block_stack_rep = repper(self.frame.block_stack)

        log.debug("  %sframe.stack: %s" % (indent, stack_rep))
        log.debug("  %sblocks     : %s" % (indent, block_stack_rep))
        log.info("%s%s" % (indent, op))

    def dispatch(self, byteName, intArg, arguments, opoffset, line_number):
        """ Dispatch by bytename to the corresponding methods.
        Exceptions are caught and set on the virtual machine."""

        why = None
        self.in_exception_processing = False
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
                if not bytecode_fn:  # pragma: no cover
                    raise PyVMError(
                        "Unknown bytecode type: %s\n\t%s"
                        % (
                            self.format_instruction(
                                self.frame,
                                self.opc,
                                byteName,
                                intArg,
                                arguments,
                                opoffset,
                                line_number,
                                False,
                            ),
                            byteName,
                        )
                    )
                why = bytecode_fn(*arguments)

        except:
            # Deal with exceptions encountered while executing the op.
            self.last_exception = sys.exc_info()

            # FIXME: dry code
            if not self.in_exception_processing:
                if self.last_exception[0] != SystemExit:
                    log.info(
                        (
                            "exception in the execution of "
                            "instruction:\n\t%s"
                            % self.format_instruction(
                                self.frame,
                                self.opc,
                                byteName,
                                intArg,
                                arguments,
                                opoffset,
                                line_number,
                                False,
                            )
                        )
                    )
                self.last_traceback = traceback_from_frame(self.frame)
                self.in_exception_processing = True

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

        if self.version < 3.0:
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

        else:
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
        if frame.f_lasti == -1:
            # We were started new, not yielded back from.
            frame.f_lasti = 0
            # Don't increment before fetching next instruction.
            frame.fallthrough = False
            byteCode = None
        else:
            byteCode = byteint(self.f_code.co_code[frame.f_lasti])
            # byteCode == opcode["YIELD_VALUE"]?

        # FIXME: we can use linestarts that is now located in the frame if this
        # is a pyvmobj.Frame, and not a native frame.
        self.frame.linestarts = dict(self.opc.findlinestarts(self.f_code, dup_lines=True))

        opoffset = 0
        while True:

            (
                byteName,
                byteCode,
                intArg,
                arguments,
                opoffset,
                line_number,
            ) = self.parse_byte_and_args(byteCode)
            if log.isEnabledFor(logging.INFO):
                self.log(byteName, intArg, arguments, opoffset, line_number)

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = self.dispatch(byteName, intArg, arguments, opoffset, line_number)
            if why == "exception":
                # TODO: ceval calls PyTraceBack_Here, not sure what that does.

                # Deal with exceptions encountered while executing the op.
                if not self.in_exception_processing:
                    # FIXME: DRY code
                    if self.last_exception[0] != SystemExit:
                        log.info(
                            (
                                "exception in the execution of "
                                "instruction:\n\t%s"
                                % self.format_instruction(
                                    frame,
                                    self.opc,
                                    byteName,
                                    intArg,
                                    arguments,
                                    opoffset,
                                line_number,
                                False,
                                )
                            )
                        )
                    self.last_traceback = traceback_from_frame(self.frame)
                    self.in_exception_processing = True

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
            if self.last_exception and self.last_exception[0]:
                six.reraise(*self.last_exception)
            else:
                raise PyVMError("Borked exception recording")
            # if self.exception and .... ?
            # log.error("Haven't finished traceback handling, nulling traceback information for now")
            # six.reraise(self.last_exception[0], None)

        self.in_exception_processing = False
        return self.return_value

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
            raise PyVMError("Unknown in-place operator: %r" % op)
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


if __name__ == "__main__":

    # Simplest of tests
    def five():
        return 5

    # Test with a conditional in it
    a, b = 10, 3

    def mymax():
        return a if a > b else b

    logging.basicConfig(level=logging.DEBUG)
    vm = PyVM()
    vm.make_frame(five.__code__)
    print(vm.run_code(five.__code__))
    print(vm.run_code(mymax.__code__, f_globals=globals(), f_locals=locals()))
    a, b = 7, 20
    print(vm.run_code(mymax.__code__, f_globals=globals(), f_locals=locals()))

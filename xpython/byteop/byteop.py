# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations base class

Note: this is subclassed. Later versions use operations from here.
"""
from __future__ import print_function, division

import inspect
import operator
import logging
import sys
from xdis import PYTHON_VERSION
from xpython.pyobj import Function
from xpython.builtins import build_class

log = logging.getLogger(__name__)

UNARY_OPERATORS = {
    "POSITIVE": operator.pos,
    "NEGATIVE": operator.neg,
    "NOT": operator.not_,
    "CONVERT": repr,
    "INVERT": operator.invert,
}

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

INPLACE_OPERATORS = frozenset([
    "ADD",
    "AND",
    "DIVIDE",
    "FLOOR_DIVIDE",
    "LSHIFT",
    "MODULO",
    "MULTIPLY",
    "OR",
    "POWER"
    "RSHIFT",
    "SUBTRACT",
    "TRUE_DIVIDE",
    "XOR",
    # 3.5 on
    "POWER",
    "MATRIX_MULTIPLY"])

if PYTHON_VERSION >= 3.5:
    BINARY_OPERATORS["MATRIX_MULTIPLY"] = operator.matmul

def fmt_binary_op(vm):
    """
    returns string of the first two elements of stack
    """
    return " (%s, %s)" % (vm.peek(1), vm.peek(2))

def fmt_unary_op(vm):
    """
    returns string of the first two elements of stack
    """
    return " (%s)" % vm.peek(1)


class ByteOpBase(object):
    def __init__(self, vm):
        self.vm = vm
        # Convenience variables
        self.version = vm.version
        self.is_pypy = vm.is_pypy
        self.PyVMError = self.vm.PyVMError

        # This is used in `vm.format_instruction()` to pick out stack elements
        # to better show operand(s) of opcode.
        self.stack_fmt = {}
        for op in BINARY_OPERATORS.keys():
            self.stack_fmt["BINARY_" + op] = fmt_binary_op
        for op in UNARY_OPERATORS.keys():
            self.stack_fmt["UNARY_" + op] = fmt_unary_op
        for op in INPLACE_OPERATORS:
            self.stack_fmt["INPLACE_" + op] = fmt_binary_op

        # Set this lazily in "convert_method_native_func
        self.method_func_access = None

    def binaryOperator(self, op):
        x, y = self.vm.popn(2)
        self.vm.push(BINARY_OPERATORS[op](x, y))

    def build_container(self, count, container_fn):
        elts = self.vm.popn(count)
        self.vm.push(container_fn(elts))

    def call_function_with_args_resolved(self, func, posargs, namedargs):
        frame = self.vm.frame
        if hasattr(func, "im_func"):
            # Methods get self as an implicit first parameter.
            if func.im_self is not None:
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

        # FIXME: should we special casing in a function?
        if inspect.isbuiltin(func):
            log.debug("handling built-in function %s" % func.__name__)
            if func == globals:
                # Use the frame's globals(), not the interpreter's
                self.vm.push(frame.f_globals)
                return
            elif func == locals:
                # Use the frame's locals(), not the interpreter's
                self.vm.push(frame.f_globals)
                return
            elif PYTHON_VERSION >= 3.0 and func == __build_class__:
                assert (
                    len(posargs) > 0
                ), "__build_class__() should have at least one argument, an __init__() function."
                if (
                    self.is_pypy or self.version != PYTHON_VERSION
                ) and PYTHON_VERSION >= 3.4:
                    # 3.4+ __build_class__() works only on bytecode that matches the CPython interpeter,
                    # so use Darius' version instead.
                    # Down the line we will try to do this universally, but it is tricky:
                    retval = build_class(self.vm.opc, *posargs, **namedargs)
                    self.vm.push(retval)
                    return
                else:
                    # Use builtin __build_class__(). However for that, we need a native function.
                    # This is wrong though in that we won't trace into __init__().
                    init_fn = posargs[0]
                    if isinstance(init_fn, Function) and init_fn in self.vm.fn2native:
                        posargs[0] = self.vm.fn2native[init_fn]

        if inspect.isfunction(func):
            # Try to convert to an interpreter function so we can interpret it.
            if func in self.vm.fn2native:
                func = self.vm.fn2native[func]
            elif False:  # self.vm.version < 3.0:
                # Not quite ready. See 3.7 test_asyncgen.py for an
                # example of code that comes here. In that test, the
                # LOAD_GLOBAL '_ignore_deprecated_imports' fails to
                # find the global. '_ignore_deprecated_imports' is a method name
                # in test.support module of test/support/__init__.py.
                # In Python 2.X we work around a similar problem by
                # not tying to handle functions with closures.
                assert len(posargs) > 0
                posargs[0] = self.convert_native_to_Function(frame, posargs[0])

        if inspect.isfunction(func):
            log.debug("calling native function %s" % func.__name__)

        retval = func(*posargs, **namedargs)
        self.vm.push(retval)

    def call_function(self, argc, args, kwargs):
        namedargs = {}
        lenKw, lenPos = divmod(argc, 256)
        for i in range(lenKw):
            key, val = self.vm.popn(2)
            namedargs[key] = val
        namedargs.update(kwargs)
        posargs = self.vm.popn(lenPos)
        posargs.extend(args)

        func = self.vm.pop()
        self.call_function_with_args_resolved(func, posargs, namedargs)

    def convert_native_to_Function(self, frame, func):
        assert inspect.isfunction(func) or isinstance(func, Function)
        slots = {
            "kwdefaults": {},
            "annotations": {},
        }
        if self.vm.version >= 3.0:
            slots["globs"] = frame.f_globals
            arg2attr = {
                "code": "__code__",
                "name": "__name__",
                "argdefs": "__defaults__",
                "kwdefaults": "__kwdefaults__",
                "annotations": "__annotations__",
                "closure": "__closure__",
                # FIXME: add __qualname__, __doc__
                # and __module__
            }
        else:
            slots["kwdefaults"] = {}
            slots["annotations"] = {}
            arg2attr = {
                "code": "func_code",
                "name": "__name__",
                "argdefs": "func_defaults",
                "globs": "func_globals",
                "annotations": "doesn't exist",
                "closure": "func_closure",
                # FIXME: add __doc__
                # and __module__
            }

        for argname, attribute in arg2attr.items():
            if hasattr(func, attribute):
                slots[argname] = getattr(func, attribute)

        closure = getattr(func, arg2attr["closure"])
        if not closure:
            # FIXME: we don't know how to convert functions with closures yet.
            native_func = func

            func = Function(
                slots["name"],
                slots["code"],
                slots["globs"],
                slots["argdefs"],
                slots["closure"],
                self.vm,
                slots["kwdefaults"],
                slots["annotations"],
            )
            self.vm.fn2native[native_func] = func
        return func

    def do_raise(self, exc, cause):
        if exc is None:  # reraise
            exc_type, val, tb = self.vm.last_exception
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

        self.vm.last_exception = exc_type, val, val.__traceback__
        return "exception"

    def inplaceOperator(self, op):
        x, y = self.vm.popn(2)
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
            raise self.PyVMError("Unknown in-place operator: %r" % op)
        self.vm.push(x)

    def lookup_name(self, name):
        """Returns the value in the current frame associated for name"""
        frame = self.vm.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        return val

    def print_item(self, item, to=None):
        if to is None:
            to = sys.stdout

        # Python 2ish has file.softspace whereas
        # Python 3ish doesn't. Here is the doc on softspace:

        # Boolean that indicates whether a space character needs to be
        # printed before another value when using the print
        # statement. Classes that are trying to simulate a file object
        # should also have a writable softspace attribute, which
        # should be initialized to zero. This will be automatic for
        # most classes implemented in Python (care may be needed for
        # objects that override attribute access); types implemented
        # in C will have to provide a writable softspace attribute.

        # Note This attribute is not used to control the print
        # statement, but to allow the implementation of print to keep
        # track of its internal state.
        if hasattr(to, "softspace") and to.softspace:
            print(" ", end="", file=to)
            to.softspace = 0
        print(item, end="", file=to)

        if hasattr(to, "softspace"):
            if isinstance(item, str):
                if (not item) or (not item[-1].isspace()) or (item[-1] == " "):
                    to.softspace = 1
            else:
                to.softspace = 1

    def print_newline(self, to=None):
        if to is None:
            to = sys.stdout
        print("", file=to)
        if hasattr(to, "softspace"):
            to.softspace = 0

    def unaryOperator(self, op):
        x = self.vm.pop()
        self.vm.push(UNARY_OPERATORS[op](x))

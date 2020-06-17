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

INPLACE_OPERATORS = frozenset(
    [
        "ADD",
        "AND",
        "DIVIDE",
        "FLOOR_DIVIDE",
        "LSHIFT",
        "MODULO",
        "MULTIPLY",
        "OR",
        "POWER" "RSHIFT",
        "SUBTRACT",
        "TRUE_DIVIDE",
        "XOR",
        # 3.5 on
        "POWER",
        "MATRIX_MULTIPLY",
    ]
)

if PYTHON_VERSION >= 3.5:
    BINARY_OPERATORS["MATRIX_MULTIPLY"] = operator.matmul


def fmt_binary_op(vm, arg=None, repr=repr):
    """returns a string of the repr() for each of the the first two
    elements of evaluation stack

    """
    return " (%s, %s)" % (repr(vm.peek(2)), repr(vm.top()))


def fmt_ternary_op(vm, arg=None, repr=repr):
    """returns string of the repr() for each of the first three
    elements of evaluation stack
    """
    return " (%s, %s, %s)" % (repr(vm.peek(3)), repr(vm.peek(2)), repr(vm.top()))


def fmt_unary_op(vm, arg=None, repr=repr):
    """returns string of the repr() for the first element of
    the evaluation stack
    """
    # We need to check the length because sometimes in a return event
    # (as opposed to a
    # a RETURN_VALUE callback can* the value has been popped, and if the
    # return valuse was the only one on the stack, it will be empty here.
    if len(vm.frame.stack):
        return " (%s)" % (repr(vm.top()),)
    else:
        raise vm.PyVMError("Empty stack in unary op")


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

    def call_function_with_args_resolved(self, func, pos_args, named_args):
        frame = self.vm.frame
        if hasattr(func, "im_func"):
            # Methods get self as an implicit first parameter.
            if func.im_self is not None:
                pos_args.insert(0, func.im_self)
            # The first parameter must be the correct type.
            if not isinstance(pos_args[0], func.im_class):
                raise TypeError(
                    "unbound method %s() must be called with %s instance "
                    "as first argument (got %s instance instead)"
                    % (
                        func.im_func.func_name,
                        func.im_class.__name__,
                        type(pos_args[0]).__name__,
                    )
                )
            func = func.im_func

        # FIXME: put this in a separate routine.
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
            elif func == compile:
                # Set dont_inherit parameter.
                # FIXME: we should set other flags too based on the interpreted environment?
                if len(pos_args) < 5 and "dont_inherit" not in named_args:
                    named_args["dont_inherit"] = True
                    pass
            # In Python 3.0 or greater, "exec()" is a builtin.  In
            # Python 2.7 it was an opcode EXEC_STMT and is not a
            # built-in function.
            #
            # FIXME: a better test would be nice. There can be
            # other builtin "exec"s. Tk has a built-in "eval". See 3.6.10
            # test_tcl.py.
            # If we drop the requirement of supporting 2.7 we can do the simpler
            # and more reliable:
            #   func == exec
            elif func.__name__ == "exec":

                if not 1 <= len(pos_args) <= 3:
                    raise self.vm.PyVMError(
                        "exec() builtin should have 1..3 positional arguments; got %d"
                        % (len(pos_args,))
                    )
                n = len(pos_args)
                assert 1 <= n <= 3

                # Note that in contrast to `eval()` handled below, if
                # the `locals` parameter is not provided, the
                # `globals` parameter value (whether provided or
                # default value) is used for the `locals`
                # parameter. So we shouldn't use the frame's `locals`.
                if len(pos_args) == 1:
                    pos_args.append(self.vm.frame.f_globals)

                if self.version == PYTHON_VERSION:
                    source = pos_args[0]
                    if isinstance(source, str):
                        try:
                            pos_args[0] = compile(
                                source, "<string>", mode="exec", dont_inherit=True
                            )
                        except (TypeError, SyntaxError, ValueError):
                            raise
                    self.vm.push(self.vm.run_code(*pos_args, toplevel=False))
                    return
                else:
                    log.warning(
                        "Running built-in `exec()` because we are cross-version interpreting version %s from version %s"
                        % (self.version, PYTHON_VERSION)
                    )

            elif func == eval:

                if not 1 <= len(pos_args) <= 3:
                    raise self.vm.PyVMError(
                        "eval() builtin should have 1..3 positional arguments; got %d"
                        % (len(pos_args,))
                    )
                assert 1 <= len(pos_args) <= 3
                # Use the frame's globals(), not the interpreter's
                n = len(pos_args)
                if n < 2:
                    pos_args.append(self.vm.frame.f_globals)
                # Likewise for locals()
                if n < 3:
                    pos_args.append(self.vm.frame.f_locals)
                assert len(pos_args) == 3

                if self.version == PYTHON_VERSION:
                    source = pos_args[0]
                    if isinstance(source, str):
                        try:
                            pos_args[0] = compile(
                                source, "<string>", mode="eval", dont_inherit=True
                            )
                        except (TypeError, SyntaxError, ValueError):
                            raise
                    self.vm.push(self.vm.run_code(*pos_args, toplevel=False))
                    return
                else:
                    log.warning(
                        "Running built-in `eval()` because we are cross-version interpreting version %s from version %s"
                        % (self.version, PYTHON_VERSION)
                    )

            elif PYTHON_VERSION >= 3.0 and func == __build_class__:
                assert (
                    len(pos_args) > 0
                ), "__build_class__() should have at least one argument, an __init__() function."
                init_fn = pos_args[0]
                if (
                    isinstance(init_fn, Function)
                    or self.is_pypy
                    or self.version != PYTHON_VERSION
                ) and PYTHON_VERSION >= 3.4:
                    # 3.4+ __build_class__() works only on bytecode that matches the CPython interpeter,
                    # so use Darius' version instead.
                    # Down the line we will try to do this universally, but it is tricky:
                    retval = build_class(self.vm.opc, *pos_args, **named_args)
                    self.vm.push(retval)
                    return
                else:
                    # Use builtin __build_class__(). However for that, we need a native function.
                    # This is wrong though in that we won't trace into __init__().
                    init_fn = pos_args[0]
                    if isinstance(init_fn, Function) and init_fn in self.vm.fn2native:
                        pos_args[0] = self.vm.fn2native[init_fn]
        elif func == type and len(pos_args) == 3:
            # Set __module__
            assert not named_args
            namespace = pos_args[2]
            namespace["__module__"] = namespace.get(
                "__name__", self.vm.frame.f_globals["__name__"]
            )

        if inspect.isfunction(func) and self.version == PYTHON_VERSION:
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
                assert len(pos_args) > 0
                pos_args[0] = self.convert_native_to_Function(frame, pos_args[0])

        if inspect.isfunction(func) and self.version == PYTHON_VERSION:
            log.debug("calling native function %s" % func.__name__)

        retval = func(*pos_args, **named_args)
        self.vm.push(retval)

    def call_function(self, argc, var_args, keyword_args):
        named_args = {}
        len_kw, len_pos = divmod(argc, 256)
        for i in range(len_kw):
            key, val = self.vm.popn(2)
            named_args[key] = val
        named_args.update(keyword_args)
        pos_args = self.vm.popn(len_pos)
        pos_args.extend(var_args)

        func = self.vm.pop()
        self.call_function_with_args_resolved(func, pos_args, named_args)

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
        elif op == "DIVIDE":
            # Overwritten __div__ is not picked up by x //= y
            # which seems to puck up FLOOR_DIVIDE
            # See Python 2.7 test_augassign.py
            if hasattr(x, "__idiv__"):
                x = x.__idiv__(y)
            else:
                x //= y
        elif op == "FLOOR_DIVIDE":
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

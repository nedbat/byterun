# Copyright (C) 2021 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.
"""Bytecode Interpreter operations for PyPy 3.7
"""
from xpython.byteop.byteop37 import ByteOp37
from xpython.byteop.byteoppypy import ByteOpPyPy


def fmt_call_method(vm, argc: int, repr=repr) -> str:
    """
    formats function name (without enclosing object), and positional args.
    """
    pos_args = [vm.peek(i + 1) for i in range(argc)]

    fn_name = vm.peek(argc + 2).__name__
    return f""" {fn_name}({", ".join((repr(a) for a in pos_args))})"""


def fmt_call_method_kw(vm, argc: int, repr=repr) -> str:
    """
    formats function name (without enclosing object), positional  and keyword args.
    """
    kwarg_names = vm.peek(1)
    kwargs_count = len(kwarg_names)
    kwargs_list = []
    for i in range(kwargs_count):
        kwargs_list.append(f"{kwarg_names[i]}={vm.peek(i+1)}")

    pos_args = []
    j = kwargs_count + 2
    for i in range(argc - kwargs_count):
        pos_args.append(vm.peek(i + j))

    fn_name = vm.peek(argc + 3).__name__
    return f""" {fn_name}({", ".join((repr(a) for a in pos_args + kwargs_list))})"""


class ByteOp37PyPy(ByteOp37, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp37PyPy, self).__init__(vm)

        self.stack_fmt["CALL_METHOD"] = fmt_call_method
        self.stack_fmt["CALL_METHOD_KW"] = fmt_call_method_kw

        self.is_pypy = True
        self.version = "3.7.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

    def CALL_METHOD_KW(self, argc: int):
        """
        argc has a count of the number of keyword parameters.
        TOS has a tuple of keyword parameter names. Below that are the
        keyword values. After that is the a cached method which in our
        case is garbage. After that is the method to call.
        """

        # We are going to access parameter off of the stack which is
        # has the last parameter closest to the top.
        # Reverse keyword names in the tuple match our access pattern.
        kw_names = self.vm.pop()
        assert isinstance(kw_names, tuple)
        kw_names = list(reversed(kw_names))
        kwarg_count = len(kw_names)

        assert argc >= kwarg_count
        pos_argc = argc - kwarg_count
        keyword_args = {}

        for i in range(kwarg_count):
            param_value = self.vm.pop()
            keyword_args[kw_names[i]] = param_value

        pos_args = []
        for i in range(pos_argc):
            pos_args.append(self.vm.pop())

        pos_args = list(reversed(pos_args))

        self.vm.pop()  # cached method slot is not used here.
        func = self.vm.pop()
        return self.call_function_with_args_resolved(func, pos_args, keyword_args)

# Copyright (C) 2021 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.
"""Bytecode Interpreter operations for PyPy 3.7
"""
from xpython.byteop.byteop37 import ByteOp37
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp37PyPy(ByteOp37, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp37PyPy, self).__init__(vm)
        self.is_pypy = True
        self.version = "3.7.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

    def CALL_METHOD_KW(self, keyword_count: int):
        """
        argc has a count of the number of keyword parameters.
        TOS has a tuple of keyword parameter names. Below that are the
        keyword values. After that is the a cached method which in our
        case is garbage. After that is the method to call.
        """
        kw_keys = self.vm.pop()
        assert isinstance(kw_keys, tuple)
        assert len(kw_keys) == keyword_count
        keyword_args = {}
        for i in range(keyword_count):
            param_value = self.vm.pop()
            keyword_args[kw_keys[i]] = param_value

        self.vm.pop()  # cached method slot is not used here.
        return self.call_function(0, var_args=[], keyword_args=keyword_args)

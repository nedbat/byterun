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
        self.version = "3.7.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

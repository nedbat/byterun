"""Bytecode Interpreter operations for PyPy 3.7
"""
from __future__ import print_function, division

from xpython.byteop.byteop37 import ByteOp37
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp37PyPy(ByteOp37, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp37PyPy, self).__init__(vm)
        self.version = "3.7.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

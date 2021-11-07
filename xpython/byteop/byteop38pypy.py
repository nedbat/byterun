"""Bytecode Interpreter operations for PyPy 3.8
"""
from __future__ import print_function, division

from xpython.byteop.byteop38 import ByteOp38
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp38PyPy(ByteOp38, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp38PyPy, self).__init__(vm)
        self.version = "3.8.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

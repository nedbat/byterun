"""Bytecode Interpreter operations for PyPy 3.2
"""
from __future__ import print_function, division

from xpython.byteop.byteop32 import ByteOp32
from xpython.byteop.byteoppypy import ByteOpPyPy

class ByteOp32PyPy(ByteOp32, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp32PyPy, self).__init__(vm)

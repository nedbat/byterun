"""Bytecode Interpreter operations for PyPy Python 2.7
"""
from __future__ import print_function, division

from xpython.byteop.byteop27 import ByteOp27
from xpython.byteop.byteoppypy import ByteOpPyPy

# Gone from 2.7
# del ByteOp25.JUMP_IF_FALSE
# del ByteOp25.JUMP_IF_TRUE


class ByteOp27PyPy(ByteOp27, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp27PyPy, self).__init__(vm)
        self.version = "2.7.10 (x-python)\n[PyPy]"

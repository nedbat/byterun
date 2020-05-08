"""Bytecode Interpreter operations for PYPY Python 2.6
"""
from __future__ import print_function, division

from xpython.byteop.byteop26 import ByteOp26
from xpython.byteop.byteoppypy import ByteOpPyPy

# Gone from 2.7
# del ByteOp25.JUMP_IF_FALSE
# del ByteOp25.JUMP_IF_TRUE

class ByteOp26PyPy(ByteOp26, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp26PyPy, self).__init__(vm)

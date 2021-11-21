"""Bytecode Interpreter operations for PYPY Python 2.6
"""
from xpython.byteop.byteop26 import ByteOp26
from xpython.byteop.byteoppypy import ByteOpPyPy

# Gone from 2.7
# del ByteOp25.JUMP_IF_FALSE
# del ByteOp25.JUMP_IF_TRUE


class ByteOp26PyPy(ByteOp26, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp26PyPy, self).__init__(vm)

        # Fake up version information not already faked in super.
        self.version = "2.6.9 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"
        self.is_pypy = True

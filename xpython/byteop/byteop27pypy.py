"""Bytecode Interpreter operations for PyPy Python 2.7
"""
from xpython.byteop.byteop27 import ByteOp27
from xpython.byteop.byteoppypy import ByteOpPyPy

# Gone from 2.7
# del ByteOp25.JUMP_IF_FALSE
# del ByteOp25.JUMP_IF_TRUE


class ByteOp27PyPy(ByteOp27, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp27PyPy, self).__init__(vm)

        # Fake up version information not already faked in super.
        self.version = "2.7.13 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"
        self.is_pypy = True

"""Bytecode Interpreter operations for PyPy 3.5
"""
from xpython.byteop.byteop35 import ByteOp35
from xpython.byteop.byteop36 import ByteOp36
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp35PyPy(ByteOp35, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp35PyPy, self).__init__(vm)

        # Fake up version information not already faked in super.
        self.version = "3.5.3 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"
        self.is_pypy = True

    # PyPy 3.5 seems to include 3.6 fstrings
    FORMAT_VALUE = ByteOp36.FORMAT_VALUE
    BUILD_STRING = ByteOp36.BUILD_STRING

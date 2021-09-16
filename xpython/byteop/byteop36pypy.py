"""Bytecode Interpreter operations for PyPy 3.6
"""
from __future__ import print_function, division

from xpython.byteop.byteop36 import ByteOp36
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp36PyPy(ByteOp36, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp36PyPy, self).__init__(vm)

        # Fake up version information not already faked in super.
        self.version = "3.6.9 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

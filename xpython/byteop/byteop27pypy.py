"""Bytecode Interpreter operations for Python 2.7
"""
from __future__ import print_function, division

from xpython.byteop.byteop27 import ByteOp27

# Gone from 2.7
# del ByteOp25.JUMP_IF_FALSE
# del ByteOp25.JUMP_IF_TRUE

class ByteOp27PyPy(ByteOp27):
    def __init__(self, vm):
        super(ByteOp27, self).__init__(vm)

    # In PyPy 2.7 but not CPython 2.7

    def LOOKUP_METHOD(self, count):
        """
        """
        raise self.vm.VMError("LOOKUP_METHOD not implemented yet")

    def CALL_METHOD(self, count):
        """
        """
        raise self.vm.VMError("CALL_METHOD not implemented yet")

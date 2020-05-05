"""Bytecode Interpreter operations for Python 3.7
"""
from __future__ import print_function, division

from xpython.byteop.byteop36 import ByteOp36

# Gone in 3.7
del ByteOp36.STORE_ANNOTATION
# del ByteOp36.WITH_CLEANUP_START
# del ByteOp36.WITH_CLEANUP_FINISH
# del ByteOp36.END_FINALLY
# del ByteOp36.POP_EXCEPT
# del ByteOp36.SETUP_WITH
# del ByteOp36.SETUP_ASYNC_WITH

class ByteOp37(ByteOp36):
    def __init__(self, vm, version=3.7):
        self.vm = vm
        self.version = version

    # Changed in 3.7

    # WITH_CLEANUP_START
    # WITH_CLEANUP_FINISH
    # END_FINALLY
    # POP_EXCEPT
    # SETUP_WITH
    # SETUP_ASYNC_WITH

    # New in 3.7

    def LOAD_METHOD(self, count):
        raise self.vm.VirtualMachineError("LOAD_METHOD not implemented yet")

    def CALL_METHOD(self, count):
        raise self.vm.VirtualMachineError("CALL_METHOD not implemented yet")

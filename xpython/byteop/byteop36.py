"""Bytecode Interpreter operations for Python 3.5
"""
from __future__ import print_function, division

from xpython.byteop.byteop25 import ByteOp25
from xpython.byteop.byteop35 import ByteOp35

# Gone in 3.6
del ByteOp25.MAKE_CLOSURE
del ByteOp25.CALL_FUNCTION_VAR
del ByteOp25.CALL_FUNCTION_VAR_KW

class ByteOp36(ByteOp35):
    def __init__(self, vm, version=3.6):
        self.vm = vm
        self.version = version

    # Changged in 3.6

    # def CALL_FUNCTION_KW

    # New in 3.6

    def STORE_ANNOTATION(self):
        raise self.VirtualMachineError("STORE_ANNOTATION not implemented yet")

    def SETUP_ASYNC_WITH(self):
        raise self.VirtualMachineError("SETUP_ASYNC_WITH not implemented yet")

    def FORMAT_VALUE(self):
        raise self.VirtualMachineError("FORMAT_VALUE not implemented yet")

    def BUILD_CONST_KEY_MAP(self, count):
        """
        The version of BUILD_MAP specialized for constant keys. count
        values are consumed from the stack. The top element on the
        stack contains a tuple of keys.
        """
        keys = self.vm.pop()
        values = self.vm.popn(count)
        kvs = dict(zip(keys, values))
        self.vm.push(kvs)

    def CALL_FUNCTION_EX(self):
        raise self.VirtualMachineError("CALL_FUNCTION_EX not implemented yet")

    def SETUP_ANNOTATIONS(self):
        raise self.VirtualMachineError("SETUP_ANNOTATIONS not implemented yet")

    def BUILD_STRING(self):
        raise self.VirtualMachineError("BUILD_STRING not implemented yet")

    def BUILD_TUPLE_UNPACK_WITH_CALL(self):
        raise self.VirtualMachineError("BUILD_TUPLE_UNPACK_WITH_CALL not implemented yet")

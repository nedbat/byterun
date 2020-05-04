"""Bytecode Interpreter operations for Python 3.6
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

    # Changed in 3.6

    # def CALL_FUNCTION_KW

    # New in 3.6

    def STORE_ANNOTATION(self, name):
        """
        Stores TOS as locals()['__annotations__'][co_names[namei]] = TOS.
        """
        raise self.vm.VirtualMachineError("STORE_ANNOTATION not implemented yet")

    def SETUP_ASYNC_WITH(self):
        """Creates a new frame object."""
        raise self.vm.VirtualMachineError("SETUP_ASYNC_WITH not implemented yet")

    def FORMAT_VALUE(self, flags):
        """Used for implementing formatted literal strings (f-strings). Pops
        an optional fmt_spec from the stack, then a required value. flags is
        interpreted as follows:

        * (flags & 0x03) == 0x00: value is formatted as-is.
        * (flags & 0x03) == 0x01: call str() on value before formatting it.
        * (flags & 0x03) == 0x02: call repr() on value before formatting it.
        * (flags & 0x03) == 0x03: call ascii() on value before formatting it.
        * (flags & 0x04) == 0x04: pop fmt_spec from the stack and use it, else use an empty fmt_spec.

        Formatting is performed using PyObject_Format(). The result is
        pushed on the stack.
        """
        # If we do nothing, then we are doing the identify formatting, which is good
        # enough to start off with.

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

    def CALL_FUNCTION_EX(self, flags):
        """
        Calls a callable object with variable set of positional and
        keyword arguments. If the lowest bit of flags is set, the top
        of the stack contains a mapping object containing additional
        keyword arguments. Below that is an iterable object containing
        positional arguments and a callable object to
        call. BUILD_MAP_UNPACK_WITH_CALL and
        BUILD_TUPLE_UNPACK_WITH_CALL can be used for merging multiple
        mapping objects and iterables containing arguments. Before the
        callable is called, the mapping object and iterable object are
        each “unpacked” and their contents passed in as keyword and
        positional arguments respectively. CALL_FUNCTION_EX pops all
        arguments and the callable object off the stack, calls the
        callable object with those arguments, and pushes the return
        value returned by the callable object.
        """
        raise self.vm.VirtualMachineError("CALL_FUNCTION_EX not implemented yet")

    def SETUP_ANNOTATIONS(self):
        """
        Checks whether __annotations__ is defined in locals(), if not it
        is set up to an empty dict. This opcode is only emitted if a
        class or module body contains variable annotations
        statically.
        """
        raise self.vm.VirtualMachineError("SETUP_ANNOTATIONS not implemented yet")

    def BUILD_STRING(self, count):
        """
        The version of BUILD_MAP specialized for constant keys. count
        values are consumed from the stack. The top element on the
        stack contains a tuple of keys.
        """
        values = self.vm.popn(count)
        self.vm.push(''.join(values))

    def BUILD_TUPLE_UNPACK_WITH_CALL(self, count):
        """
        This is similar to BUILD_TUPLE_UNPACK, but is used for f(*x, *y,*z)
        call syntax. The stack item at position count + 1 should be the
        corresponding callable f.
        """
        raise self.vm.VirtualMachineError("BUILD_TUPLE_UNPACK_WITH_CALL not implemented yet")

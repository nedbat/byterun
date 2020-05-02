"""Bytecode Interpreter operations for Python 3.5
"""
from __future__ import print_function, division

import inspect
import types

from xpython.byteop.byteop25 import ByteOp25
from xpython.byteop.byteop33 import ByteOp33
from xpython.byteop.byteop34 import ByteOp34

# Gone in 3.5
del ByteOp25.STORE_MAP
del ByteOp33.WITH_CLEANUP

class ByteOp35(ByteOp34):
    def __init__(self, vm):
        self.vm = vm
        self.version = 3.5

    # Changed in 3.5

    def BUILD_MAP(self, count):
        """
        Pushes a new dictionary object onto the stack. Pops 2 * count
        items so that the dictionary holds count entries: {..., TOS3:
        TOS2, TOS1: TOS}.

        Changed in version 3.5: The dictionary is created from stack
        items instead of creating an empty dictionary pre-sized to
        hold count items.
        """
        kvs = self.vm.popn(count * 2)
        self.vm.push(dict(kvs[i:i+2] for i in range(0, len(kvs), 2)))

    # New in 3.5

    def BUILD_TUPLE_UNPACK(self, count):
        """
        Pops count iterables from the stack, joins them in a single tuple,
        and pushes the result. Implements iterable unpacking in
        tuple displays (*x, *y, *z).
        """
        elts = self.vm.popn(count)
        self.vm.push(tuple(e for l in elts for e in l))

    def BUILD_LIST_UNPACK(self, count):
        """
        This is similar to BUILD_TUPLE_UNPACK, but pushes a list instead of tuple.
        Implements iterable unpacking in list displays [*x, *y, *z].
        """
        elts = self.vm.popn(count)
        self.vm.push(list(e for l in elts for e in l))

    def BUILD_SET_UNPACK(self, count):
        """
        Pops count mappings from the stack, merges them into a single
        dictionary, and pushes the result. Implements dictionary
        unpacking in dictionary displays {**x, **y, **z}.
        """
        elts = self.vm.popn(count)
        self.vm.push(set(e for l in elts for e in l))

    def BUILD_MAP_UNPACK(self, count):
        """
        Pops count iterables from the stack, joins them in a single tuple,
        and pushes the result. Implements iterable unpacking in
        tuple displays (*x, *y, *z).
        """
        elts = self.vm.popn(count)
        self.vm.push({k:v for m in elts for k, v in m.items()})

    def BUILD_MAP_UNPACK_WITH_CALL(self, oparg):
        """
        This is similar to BUILD_MAP_UNPACK, but is used for f(**x, **y,
        **z) call syntax. The lowest byte of oparg is the count of
        mappings, the relative position of the corresponding callable
        f is encoded in the second byte of oparg.
        """
        arg, count = divmod(arg, 256)
        elts = self.vm.popn(count)
        kwargs = {k:v for m in elts for k, v in m.items()}
        # FIXME: This is probably not right
        self.vm.call_function(arg, 0, kwargs)


        def GET_AITER(self):
            raise self.VirtualMachineError("GET_AITER not implemented yet")

        def GET_ANEXT(self):
            raise self.VirtualMachineError("GET_ANEXT not implemented yet")

        def BEFORE_ASYNC_WITH(self):
            raise self.VirtualMachineError("BEFORE_ASYNC_WITH not implemented yet")
            return

        def GET_YIELD_FROM_ITER(self):
            raise self.VirtualMachineError("GET_YIELD_FROM_ITER not implemented yet")

        def GET_AWAITABLE(self):
            raise self.VirtualMachineError("GET_AWAITABLE not implemented yet")

        def WITH_CLEANUP_START(self):
            raise self.VirtualMachineError("WITH_CLEANUP_START not implemented yet")

        def WITH_CLEANUP_FINISH(self):
            raise self.VirtualMachineError("WITH_CLEANUP_FINISH not implemented yet")

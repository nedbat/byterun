"""Bytecode Interpreter operations for Python 3.5
"""
from __future__ import print_function, division

import types
from xpython.byteop.byteop25 import ByteOp25
from xpython.byteop.byteop32 import ByteOp32
from xpython.byteop.byteop34 import ByteOp34

# Gone in 3.5
del ByteOp25.STORE_MAP
del ByteOp32.WITH_CLEANUP


class ByteOp35(ByteOp34):
    def __init__(self, vm):
        super(ByteOp35, self).__init__(vm)

    def build_container_flat(self, count, container_fn):
        elts = self.vm.popn(count)
        self.vm.push(container_fn(e for l in elts for e in l))

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
        self.vm.push(dict(kvs[i : i + 2] for i in range(0, len(kvs), 2)))

    # New in 3.5

    def BUILD_TUPLE_UNPACK(self, count):
        """
        Pops count iterables from the stack, joins them in a single tuple,
        and pushes the result. Implements iterable unpacking in
        tuple displays (*x, *y, *z).
        """
        self.build_container_flat(count, tuple)

    def BUILD_LIST_UNPACK(self, count):
        """
        This is similar to BUILD_TUPLE_UNPACK, but pushes a list instead of tuple.
        Implements iterable unpacking in list displays [*x, *y, *z].
        """
        self.build_container_flat(count, list)

    def BUILD_SET_UNPACK(self, count):
        """
        Pops count mappings from the stack, merges them into a single
        dictionary, and pushes the result. Implements dictionary
        unpacking in dictionary displays {**x, **y, **z}.
        """
        self.build_container_flat(count, set)

    def BUILD_MAP_UNPACK(self, count):
        """
        Pops count iterables from the stack, joins them in a single tuple,
        and pushes the result. Implements iterable unpacking in
        tuple displays (*x, *y, *z).
        """
        # Note: this isn't the same thing as build_container_flat
        elts = self.vm.popn(count)
        result = {}
        for d in elts:
            result.update(d)
        self.vm.push(result)

    def BUILD_MAP_UNPACK_WITH_CALL(self, oparg):
        """
        This is similar to BUILD_MAP_UNPACK, but is used for f(**x, **y,
        **z) call syntax. The lowest byte of oparg is the count of
        mappings, the relative position of the corresponding callable
        f is encoded in the second byte of oparg.
        """
        fn_pos, count = divmod(oparg, 256)
        elts = self.vm.popn(count)
        if elts:
            kwargs = {k: v for m in elts for k, v in m.items()}
        else:
            kwargs = None
        posargs = self.vm.pop()
        func = self.vm.pop(fn_pos)

        # Put everything in the right order for CALL_FUNCTION_EX
        self.vm.push(func)
        self.vm.push(posargs)
        if kwargs:
            self.vm.push(kwargs)

    # Coroutine opcodes

    def GET_AWAITABLE(self):
        """
        Implements TOS = get_awaitable(TOS), where get_awaitable(o)
        returns o if o is a coroutine object or a generator object
        with the CO_ITERABLE_COROUTINE flag, or resolves
        o.__await__.
        """
        # # Adapted from PyPy 3.6 v. 7.3.1
        # from xpython.interpreter.generator import get_awaitable_iter
        # from xpython.interpreter.generator import Coroutine
        # iterable = self.vm.pop()
        # iter = get_awaitable_iter(self.space, iterable)
        # if isinstance(iter, Coroutine):
        #     if iter.get_delegate() is not None:
        #         # 'w_iter' is a coroutine object that is being awaited,
        #         # '.w_yielded_from' is the current awaitable being awaited on.
        #         raise RuntimeError("coroutine is being awaited already")

        raise self.vm.PyVMError("GET_AWAITABLE not implemented yet")

    def GET_AITER(self):
        """
        Implements TOS = get_awaitable(TOS.__aiter__()). See GET_AWAITABLE
        for details about get_awaitable
        """
        raise self.vm.PyVMError("GET_AITER not implemented yet")
        # TOS = self.vm.pop()
        # self.vm.push(get_awaitable(TOS.__aiter__()))

    def GET_ANEXT(self):
        """
        Implements PUSH(get_awaitable(TOS.__anext__())). See GET_AWAITABLE
        for details about get_awaitable
        """
        raise self.vm.PyVMError("GET_ANEXT not implemented yet")
        # TOS = self.vm.pop()
        # self.vm.push(get_awaitable(TOS.__anext()))

    def BEFORE_ASYNC_WITH(self):
        raise self.vm.PyVMError("BEFORE_ASYNC_WITH not implemented yet")
        return

    def GET_YIELD_FROM_ITER(self):
        """
        If TOS is a generator iterator or coroutine object it is left as
        is. Otherwise, implements TOS = iter(TOS).
        """
        TOS = self.vm.top()
        if isinstance(TOS, types.GeneratorType) or isinstance(TOS, types.CoroutineType):
            return
        TOS = self.vm.pop()
        self.vm.push(iter(TOS))

    def WITH_CLEANUP_START(self):
        """Cleans up the stack when a with statement block exits.

        TOS is the context manager s __exit__() bound method. Below
        TOS are 1 - 3 values indicating how/why the finally clause was
        entered:

        * SECOND = None
        * (SECOND, THIRD) = (WHY_{RETURN,CONTINUE}), retval
        * SECOND = WHY_*; no retval below it
        * (SECOND, THIRD, FOURTH) = exc_info()

        In the last case, TOS(SECOND, THIRD, FOURTH) is called,
        otherwise TOS(None, None, None). Pushes SECOND and result of the call
        to the stack.  Cleans up the stack when a `with` statement block
        exits. TOS is the context manager's `__exit__()` bound method.
        """
        second = third = fourth = None
        TOS = self.vm.top()
        if TOS is None:
            exit_method = self.vm.pop(1)
        elif isinstance(TOS, str):
            # FIXME: This code does something funky with pushing "continue"
            # See the comment under CONTINUE_LOOP.
            # jump addresses on the frame stack. As a result, we need to
            # set up here something to make END_FINALLY work and remove
            # the jump address. This means that the comment or semantics
            # described above isn't strictly correct.
            if TOS in ("return", "continue"):
                exit_method = self.vm.pop(2)
            else:
                exit_method = self.vm.pop(1)
        elif issubclass(TOS, BaseException):
            fourth, third, second = self.vm.popn(3)
            tp, exc, tb = self.vm.popn(3)
            exit_method = self.vm.pop()
            self.vm.push(None)
            self.vm.push(fourth, third, second)
            block = self.vm.pop_block()
            assert block.type == "except-handler"
            self.vm.push_block(block.type, block.handler, block.level - 1)
        exit_ret = exit_method(second, third, fourth)
        self.vm.push(second)
        self.vm.push(exit_ret)

    def WITH_CLEANUP_FINISH(self):
        """Pops exception type and result of "exit" function call from the stack.

        If the stack represents an exception, and the function call
        returns a  true  value, this information is "zapped" and
        replaced with a single WHY_SILENCED to prevent END_FINALLY
        from re-raising the exception. (But non-local gotos will still
        be resumed.)
        """
        exit_ret = self.vm.pop(1)
        u = self.vm.pop()
        if type(u) is type and issubclass(u, BaseException) and exit_ret:
            self.vm.push("silenced")

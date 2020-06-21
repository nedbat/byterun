"""Bytecode Interpreter operations for Python 3.5
"""
from __future__ import print_function, division

from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop32 import ByteOp32
from xpython.byteop.byteop34 import ByteOp34
from xpython.stdlib.inspect3 import iscoroutinefunction, isgeneratorfunction

# Gone in 3.5
del ByteOp24.STORE_MAP
del ByteOp32.WITH_CLEANUP


def fmt_build_map_unpack_with_call(vm, arg, repr=repr):
    """returns string of the repr() for the first element of
    the evaluation stack
    """
    # See corresponding comment in BUILD_MAP_UNPACK_WITH_CALL
    if vm.version == 3.5:
        fn_pos, count = divmod(arg, 256)
        fn_pos = count + fn_pos
    else:
        fn_pos = arg + 1
    return " (%s)" % (repr(vm.peek(fn_pos)))


class ByteOp35(ByteOp34):
    def __init__(self, vm):
        super(ByteOp35, self).__init__(vm)
        self.stack_fmt["BUILD_MAP_UNPACK_WITH_CALL"] = fmt_build_map_unpack_with_call

    def build_container_flat(self, count, container_fn):
        elts = self.vm.popn(count)
        self.vm.push(container_fn(e for l in elts for e in l))

    def get_awaitable_iter(self, o):
        # This helper function returns an awaitable for `o`:
        #    - `o` if `o` is a coroutine-object;
        #    - otherwise, o.__await__()

        if iscoroutinefunction(o) or isgeneratorfunction(o):
            return o
        return o

        if not hasattr(o, "__await__"):
            raise TypeError("object %s can't be used in 'await' expression", o)

        # FIXME: start here
        raise self.vm.PyVMError("get_awaitable_iter() not fully implemented")
        await_fn = None
        result = self.call_function(await_fn, [o])

        if not iscoroutinefunction(o):
            raise TypeError(
                "__await__() returned a coroutine (it must return an "
                "iterator instead, see PEP 492)"
            )
        elif not hasattr(result, "__next__") or result.__next__ is None:
            raise TypeError(
                "__await__() returned non-iterator " "of type '%s'", type(result)
            )
        return result

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

    def GET_YIELD_FROM_ITER(self):
        """
        If TOS is a generator iterator or coroutine object it is left as
        is. Otherwise, implements TOS = iter(TOS).
        """
        TOS = self.vm.top()
        if isgeneratorfunction(TOS) or iscoroutinefunction(TOS):
            return
        TOS = self.vm.pop()
        self.vm.push(iter(TOS))

    # Coroutine opcodes

    def GET_AWAITABLE(self):
        """
        Implements TOS = get_awaitable(TOS), where get_awaitable(o)
        returns o if o is a coroutine object or a generator object
        with the CO_ITERABLE_COROUTINE flag, or resolves
        o.__await__.
        """
        raise self.vm.PyVMError("GET_AWAITABLE not implemented yet")
        iterable = self.vm.pop()
        iter = self.get_awaitable_iter(iterable)
        if iscoroutinefunction(iter):
            # if iter.get_delegate() is not None:
            #     # 'w_iter' is a coroutine object that is being awaited,
            #     # '.w_yielded_from' is the current awaitable being awaited on.
            #     raise RuntimeError("coroutine is being awaited already")
            pass
        self.vm.push(iter)

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
        returns a true value, this information is "zapped" and
        replaced with a single WHY_SILENCED to prevent END_FINALLY
        from re-raising the exception. (But non-local gotos will still
        be resumed.)
        """
        exit_result = self.vm.pop()
        exception = self.vm.pop()
        if (
            exit_result
            and type(exception) is type
            and issubclass(exception, BaseException)
        ):
            # Pop the exception and replace with "silenced".
            self.vm.popn(1)
            self.vm.push("silenced")
            return "silenced"

    # All of the following opcodes expect arguments. An argument is two bytes, with the more significant byte last.

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
        # In 3.5 fn_pos may be always 1 which meant the stack
        # entry after the mappings. In 3.6 this function-position
        # encoding was dropped. But we'll follow the spec.
        fn_pos, count = divmod(oparg, 256)
        fn_pos -= 1

        elts = self.vm.popn(count)
        if elts:
            kwargs = {k: v for m in elts for k, v in m.items()}
        else:
            kwargs = None
        func = self.vm.pop(fn_pos)

        # Put everything in the right order for CALL_FUNCTION_KW
        self.vm.push(func)
        if kwargs:
            self.vm.push(kwargs)

    def CALL_FUNCTION_VAR(self, argc):
        """Calls a callable object, similarly to `CALL_FUNCTION_VAR` and
        `CALL_FUNCTION_KW`. *argc* represents the number of keyword
        and positional arguments, identically to `CALL_FUNCTION`. The
        top of the stack contains a mapping object, as per
        `CALL_FUNCTION_KW`. Below that are keyword arguments (if any),
        stored identically to `CALL_FUNCTION`. Below that is an iterable
        object containing additional positional arguments. Below that
        are positional arguments (if any) and a callable object,
        identically to `CALL_FUNCTION`a. Before the callable is called,
        the mapping object and iterable object are each "unpacked" and
        their contents passed in as keyword and positional arguments
        respectively, identically to `CALL_FUNCTION_VAR` and
        `CALL_FUNCTION_KW`. The mapping object and iterable object are
        both ignored when computing the value of argc.

        Changed in version 3.5: In all Python versions 3.4, the
        iterable object (var_args) was above the keyword arguments
        (keyword_args); in 3.5 the iterable object was moved below the
        keyword arguments.

        """
        keyword_args = {}
        len_kw, len_pos = divmod(argc, 256)
        for i in range(len_kw):
            key, val = self.vm.popn(2)
            keyword_args[key] = val
        var_args = self.vm.pop()
        pos_args = self.vm.popn(len_pos)
        pos_args.extend(var_args)
        func = self.vm.pop()
        self.call_function_with_args_resolved(
            func, pos_args=pos_args, named_args=keyword_args
        )

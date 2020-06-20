"""Bytecode Interpreter operations for Python 3.6
"""
from __future__ import print_function, division

import inspect

from xdis import PYTHON_VERSION
from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop35 import ByteOp35
from xpython.pyobj import Function

# Gone in 3.6
del ByteOp24.MAKE_CLOSURE
del ByteOp24.CALL_FUNCTION_VAR
del ByteOp24.CALL_FUNCTION_KW
del ByteOp24.CALL_FUNCTION_VAR_KW

# Note the order is important. The TOS is listed *last*.
MAKE_FUNCTION_SLOT_NAMES = ("closure", "annotations", "kwdefaults", "defaults")
MAKE_FUNCTION_SLOTS = len(MAKE_FUNCTION_SLOT_NAMES)

def identity(x):
    return x


FSTRING_CONVERSION_MAP = {
    0: identity,
    1: str,
    2: repr,
}

if PYTHON_VERSION > 2.7:
    FSTRING_CONVERSION_MAP[3] = ascii

# Code with these co_names have an implicit .0 in them
COMPREHENSION_FN_NAMES = frozenset(
    ("<setcomp>", "<dictcomp>", "<genexpr>", "<listcomp>",)
)

def fmt_call_function(vm, argc, repr=repr):
    """
    returns the name of the function from the code object in the stack
    """
    TOS = vm.peek(argc + 1)
    for attr in ("co_name", "func_name", "__name__"):
        if hasattr(TOS, attr):
            return " (%s)" % getattr(TOS, attr)

    # Nothing found.
    return ""

def fmt_call_function_kw(vm, argc, repr=repr):
    """
    returns the name of the function from the code object in the stack
    """
    namedargs_tup = vm.top()
    func = vm.peek(argc + 2)
    return " (keyword: %s, function: %s)" % (namedargs_tup, func)

class ByteOp36(ByteOp35):
    def __init__(self, vm):
        super(ByteOp36, self).__init__(vm)
        self.stack_fmt["CALL_FUNCTION"] = fmt_call_function
        self.stack_fmt["CALL_FUNCTION_KW"] = fmt_call_function_kw

    def call_function_kw(self, argc):
        namedargs = {}
        namedargs_tup = self.vm.pop()
        for name in reversed(namedargs_tup):
            namedargs[name] = self.vm.pop()

        lenPos = argc - len(namedargs_tup)
        posargs = self.vm.popn(lenPos)
        func = self.vm.pop()
        self.call_function_with_args_resolved(func, posargs, namedargs)

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.6/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    # Changed in 3.6

    def BUILD_MAP_UNPACK_WITH_CALL(self, oparg):
        """
        This is similar to BUILD_MAP_UNPACK, but is used for f(**x, **y,
        **z) call syntax. The lowest byte of oparg is the count of
        mappings, the relative position of the corresponding callable
        f is encoded in the second byte of oparg.
        """
        count = oparg
        fn_pos = 0

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

    def CALL_FUNCTION_KW(self, argc):
        """
        Calls a callable object with positional (if any) and keyword
        arguments.

        argc indicates the total number of positional and
        keyword arguments. The top element on the stack contains a tuple
        of keyword argument names. Below that are keyword arguments in
        the order corresponding to the tuple. Below that are positional
        arguments, with the right-most parameter on top. Below the
        arguments is a callable object to call. CALL_FUNCTION_KW pops
        all arguments and the callable object off the stack, calls the
        callable object with those arguments, and pushes the return
        value returned by the callable object.

        Changed in version 3.6: Keyword arguments are packed in a tuple
        instead of a dictionary, argc indicates the total number of
        arguments.
        """
        return self.call_function_kw(argc)

    def MAKE_FUNCTION(self, argc):
        """
        Pushes a new function object on the stack. From bottom to top,
        the consumed stack must consist of values if the argument
        carries a specified flag value

        * 0x01 a tuple of default values for positional-only and positional-or-keyword parameters in positional order
        * 0x02 a dictionary of the default values for the keyword-only parameters
               the key is the parameter name and the value is the default value
        * 0x04 an annotation dictionary
        * 0x08 a tuple containing cells for free variables, making a closure
          the code associated with the function (at TOS1)
        * the qualified name of the function (at TOS)
        """
        qualname = self.vm.pop()
        name = qualname.split(".")[-1]
        code = self.vm.pop()

        slot = {
            "defaults": tuple(),
            "kwdefaults": {},
            "annotations": {},
            "closure": tuple(),
        }
        assert 0 <= argc < (1 << MAKE_FUNCTION_SLOTS)
        have_param = list(reversed([True if 1 << i & argc else False for i in range(4)]))
        for i in range(MAKE_FUNCTION_SLOTS):
            if have_param[i]:
                slot[MAKE_FUNCTION_SLOT_NAMES[i]] = self.vm.pop()

        # FIXME: DRY with code in byteop3{2,4}.py

        globs = self.vm.frame.f_globals

        if not inspect.iscode(code) and hasattr(code, "to_native") and self.version == PYTHON_VERSION:
            code = code.to_native()

        fn_vm = Function(
            name=name,
            qualname=qualname,
            code=code,
            globs=globs,
            argdefs=slot["defaults"],
            closure=slot["closure"],
            vm=self.vm,
            kwdefaults=slot["kwdefaults"],
            annotations=slot["annotations"],
        )

        if argc == 0 and code.co_name in COMPREHENSION_FN_NAMES:
            fn_vm.has_dot_zero = True

        if fn_vm._func:
            self.vm.fn2native[fn_vm] = fn_vm._func

        self.vm.push(fn_vm)

    # New in 3.6...

    # .. and this one is gone in 3.8
    def STORE_ANNOTATION(self, name):
        """
        Stores TOS as locals()['__annotations__'][co_names[namei]] = TOS.
        """
        self.vm.frame.f_locals["__annotations__"][name] = self.vm.pop()

    def SETUP_ASYNC_WITH(self):
        """Creates a new frame object."""
        raise self.vm.PyVMError("SETUP_ASYNC_WITH not implemented yet")

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
        if flags & 0x04 == 0x04:
            format_spec = self.vm.pop()
        else:
            format_spec = ''

        value = self.vm.pop()
        attr_flags = flags & 0x03
        if attr_flags:
            value = FSTRING_CONVERSION_MAP.get(attr_flags, identity)(value)

        result = format(value, format_spec)
        self.vm.push(result)

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
        each  unpacked  and their contents passed in as keyword and
        positional arguments respectively. CALL_FUNCTION_EX pops all
        arguments and the callable object off the stack, calls the
        callable object with those arguments, and pushes the return
        value returned by the callable object.
        """
        namedargs = self.vm.pop() if flags & 1 else {}
        posargs = self.vm.pop()
        func = self.vm.pop()
        self.call_function_with_args_resolved(func, posargs, namedargs)

    def SETUP_ANNOTATIONS(self):
        """
        Checks whether __annotations__ is defined in locals(), if not it
        is set up to an empty dict. This opcode is only emitted if a
        class or module body contains variable annotations
        statically.
        """
        if "__annotations__" not in self.vm.frame.f_locals:
            self.vm.frame.f_locals["__annotations__"] = {}

    def BUILD_STRING(self, count):
        """
        The version of BUILD_MAP specialized for constant keys. count
        values are consumed from the stack. The top element on the
        stack contains a tuple of keys.
        """
        values = self.vm.popn(count)
        self.vm.push("".join(values))

    def BUILD_TUPLE_UNPACK_WITH_CALL(self, count):
        """
        This is similar to BUILD_TUPLE_UNPACK, but is used for f(*x, *y,*z)
        call syntax. The stack item at position count + 1 should be the
        corresponding callable f.
        """
        parameter_tuples = self.vm.popn(count)
        parameters = [
            parameter for sublist in parameter_tuples for parameter in sublist
        ]
        self.vm.push(parameters)

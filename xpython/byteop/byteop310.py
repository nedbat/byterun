# -*- coding: utf-8 -*-
# Copyright (C) 2021 Rocky Bernstein
# This program comes with ABSOLUTELY NO WARRANTY.
# This is free software, and you are welcome to redistribute it
# under certain conditions.
# See the documentation for the full license.
"""Bytecode Interpreter operations for Python 3.10
"""
import inspect

from xdis.version_info import PYTHON_VERSION_TRIPLE
from xpython.byteop.byteop24 import ByteOp24, Version_info

from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop36 import (
    COMPREHENSION_FN_NAMES,
    MAKE_FUNCTION_SLOTS,
    MAKE_FUNCTION_SLOT_NAMES,
)
from xpython.byteop.byteop39 import ByteOp39
from xpython.pyobj import Function


class ByteOp310(ByteOp39):
    def __init__(self, vm):
        super(ByteOp310, self).__init__(vm)
        self.hexversion = 0x30A00F0
        self.version = "3.10.0 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 10, 0, "final", 0)

    # Changed in 3.10...
    def MAKE_FUNCTION(self, argc):
        """
        Pushes a new function object on the stack. From bottom to top,
        the consumed stack must consist of values if the argument
        carries a specified flag value

        * 0x01 a tuple of default values for positional-only and positional-or-keyword parameters in positional order
        * 0x02 a dictionary of the default values for the keyword-only parameters
               the key is the parameter name and the value is the default value
        * 0x04 a tuple of strings containing parameters  annotations
        * 0x08 a tuple containing cells for free variables, making a closure
          the code associated with the function (at TOS1)
        * the qualified name of the function (at TOS)

        Changed from version 3.6: Flag value 0x04 is a tuple of strings instead of dictionary
        """
        qualname = self.vm.pop()
        name = qualname.split(".")[-1]
        code = self.vm.pop()

        slot = {
            "defaults": tuple(),
            "kwdefaults": {},
            "annotations": tuple(),
            "closure": tuple(),
        }
        assert 0 <= argc < (1 << MAKE_FUNCTION_SLOTS)
        have_param = list(
            reversed([True if 1 << i & argc else False for i in range(4)])
        )
        for i in range(MAKE_FUNCTION_SLOTS):
            if have_param[i]:
                slot[MAKE_FUNCTION_SLOT_NAMES[i]] = self.vm.pop()

        # FIXME: DRY with code in byteop3{2,4,6}.py

        globs = self.vm.frame.f_globals

        if (
            not inspect.iscode(code)
            and hasattr(code, "to_native")
            and self.version_info[:2] == PYTHON_VERSION_TRIPLE[:2]
        ):
            code = code.to_native()

        # Convert annotations tuple into dictionary
        annotations = {}
        annotations_tup = slot["annotations"]
        for i in range(0, len(annotations_tup), 2):
            annotations[annotations_tup[i]] = annotations_tup[i + 1]

        fn_vm = Function(
            name=name,
            qualname=qualname,
            code=code,
            globs=globs,
            argdefs=slot["defaults"],
            closure=slot["closure"],
            vm=self.vm,
            kwdefaults=slot["kwdefaults"],
            annotations=annotations,
        )

        if argc == 0 and code.co_name in COMPREHENSION_FN_NAMES:
            fn_vm.has_dot_zero = True

        if fn_vm._func:
            self.vm.fn2native[fn_vm] = fn_vm._func

        self.vm.push(fn_vm)

    # New in 3.10

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.10/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    def COPY_DICT_WITHOUT_KEYS(self):
        """TOS is a tuple of mapping keys, and TOS1 is the match
        subject. Replace TOS with a dict formed from the items of TOS1, but
        without any of the keys in TOS."""
        # FIXME
        raise self.vm.PyVMError("MATCH_COPY_DICT_WITHOUT_KEYS not implemented")

    def GET_LEN(self):
        """Push len(TOS) onto the stack."""
        self.vm.push(len(self.vm.pop()))

    def MATCH_MAPPING(self):
        """If TOS is an instance of collections.abc.Mapping (or, more
        technically: if it has the Py_TPFLAGS_MAPPING flag set in its
        tp_flags), push True onto the stack. Otherwise, push False.
        """
        # FIXME
        raise self.vm.PyVMError("MATCH_MAPPING not implemented")

    def MATCH_SEQUENCE(self):
        """If TOS is an instance of collections.abc.Sequence and is not an
        instance of str/bytes/bytearray (or, more technically: if it
        has the Py_TPFLAGS_SEQUENCE flag set in its tp_flags), push
        True onto the stack. Otherwise, push False.
        """
        # FIXME
        raise self.vm.PyVMError("MATCH_SEQUENCE not implemented")

    def MATCH_KEYS(self):
        """TOS is a tuple of mapping keys, and TOS1 is the match subject. If
        TOS1 contains all of the keys in TOS, push a tuple containing
        the corresponding values, followed by True. Otherwise, push
        None, followed by False.
        """
        # FIXME
        raise self.vm.PyVMError("MATCH_KEYS not implemented")

    def GEN_START(self, kind):
        """Pops TOS. If TOS was not None, raises an exception. The kind
        operand corresponds to the type of generator or coroutine and
        determines the error message. The legal kinds are 0 for
        generator, 1 for coroutine, and 2 for async generator.
        """
        generator = self.vm.pop()
        # if generator is None:
        #     raise self.vm.PyVMError("GEN_START TOS is None")
        # FIXME
        assert kind in (0, 1, None)

    def ROT_N(self, count: int):
        """
        Lift the top count stack items one position up, and move TOS down to position count.
        """
        # FIXME
        raise self.vm.PyVMError("ROT_N not implemented")

    def MATCH_CLASS(self):
        """TOS is a tuple of keyword attribute names, TOS1 is the class being
        matched against, and TOS2 is the match subject. count is the number of
        positional sub-patterns.

        Pop TOS. If TOS2 is an instance of TOS1 and has the positional
        and keyword attributes required by count and TOS, set TOS to
        True and TOS1 to a tuple of extracted attributes. Otherwise,
        set TOS to False.
        """
        # FIXME
        raise self.vm.PyVMError("MATCH_CLASS not implemented")

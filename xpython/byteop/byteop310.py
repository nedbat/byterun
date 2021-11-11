# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 3.10
"""
from xpython.byteop.byteop24 import Version_info
from xpython.byteop.byteop39 import ByteOp39


class ByteOp310(ByteOp39):
    def __init__(self, vm):
        super(ByteOp310, self).__init__(vm)
        self.hexversion = 0x30A00F0
        self.version = "3.10.0 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(3, 10, 0, "final", 0)

    # Changed in 3.10...

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
        # FIXME
        assert kind in (0, 1, None)
        self.vm.pop()
        raise self.vm.PyVMError("GEN_START not implemented")

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

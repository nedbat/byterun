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

    def GET_LEN(self):
        # FIXME
        raise self.vm.PyVMError("GET_LEN not implemented")

    def MATCH_MAPPING(self):
        # FIXME
        raise self.vm.PyVMError("MATCH_MAPPING not implemented")

    def MATCH_SEQUENCE(self):
        # FIXME
        raise self.vm.PyVMError("MATCH_SEQUENCE not implemented")

    def MATCH_KEYS(self):
        # FIXME
        raise self.vm.PyVMError("MATCH_KEYS not implemented")

    def COPY_DICT_WITHOUT_KEYS(self):
        # FIXME
        raise self.vm.PyVMError("MATCH_COPY_DICT_WITHOUT_KEYS not implemented")

    def ROT_N(self):
        # FIXME
        raise self.vm.PyVMError("ROT_N not implemented")

    def GEN_START(self):
        # FIXME
        raise self.vm.PyVMError("GEN_START not implemented")

    def MATCH_CLASS(self):
        # FIXME
        raise self.vm.PyVMError("MATCH_CLASS not implemented")

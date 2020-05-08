"""Bytecode Interpreter operations for PyPy in general (all versions)

Specific PyPy versions i.e. PyPy 2.7, 3.2, 3.5, and 3.6 inherit this.
"""
from __future__ import print_function, division


class ByteOpPyPy(object):
    def LOOKUP_METHOD(self, count):
        """
        """
        raise self.vm.VMError("LOOKUP_METHOD not implemented yet")

    def CALL_METHOD(self, count):
        """
        """
        raise self.vm.VMError("CALL_METHOD not implemented yet")

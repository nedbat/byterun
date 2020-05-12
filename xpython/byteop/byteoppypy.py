"""Bytecode Interpreter operations for PyPy in general (all versions)

Specific PyPy versions i.e. PyPy 2.7, 3.2, 3.5, and 3.6 inherit this.
"""
from __future__ import print_function, division


class ByteOpPyPy(object):
    def LOOKUP_METHOD(self, name):
        """
        For now, we'll assume this is the same as LOAD_ATTR:

        Replaces TOS with getattr(TOS, co_names[namei]).
        Note: name = co_names[namei] set in parse_byte_and_args()

        """
        obj = self.vm.pop()
        val = getattr(obj, name)
        self.vm.push(val)

    def CALL_METHOD(self, argc):
        """
        For now, we'll assume this is like CALL_FUNCTION:

        Calls a callable object.
        The low byte of argc indicates the number of positional
        arguments, the high byte the number of keyword arguments.
        ...
        """
        return self.call_function(argc, [], {})

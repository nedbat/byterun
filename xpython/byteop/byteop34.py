"""Bytecode Interpreter operations for Python 3.4
"""
from __future__ import print_function, division

import six
import sys
import operator
import types

from xpython.byteop.byteop33 import ByteOp33

# Gone since 3.3
del ByteOp33.STORE_LOCALS

class ByteOp34(ByteOp33):
    def __init__(self, vm):
        self.vm = vm
        self.version = 3.4

    # New in 3.4

    def LOAD_CLASSDEREF(self, count):
        """
        Much like LOAD_DEREF but first checks the locals dictionary before
        consulting the cell. This is used for loading free variables in class
        bodies.
        """
        self.vm.push(self.vm.frame.cells[i].get())


    # Changed in 3.4

    # Python 3.4 __build_class__ is more strict about what can be a
    # function type whereas in earlier version we could get away with
    # our own kind of xpython.pyobj.Function object.
    #
    def MAKE_FUNCTION(self, argc):
        name = self.vm.pop()
        code = self.vm.pop()
        defaults = self.vm.popn(argc)
        globs = self.vm.frame.f_globals

        # FIXME: we should test PYTHON_VERSION to check for sanity.
        fn = types.FunctionType(code, globs, name, tuple(defaults))
        fn.version = self.version # This is our extra tagging.
        self.vm.push(fn)

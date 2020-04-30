"""Bytecode Interpreter operations for Python 3.4
"""
from __future__ import print_function, division

import six
import sys
import operator

from xpython.byteop.byteop33 import ByteOp33

# Gone since 3.3
del ByteOp33.STORE_LOCALS

class ByteOp34(ByteOp33):
    def __init__(self, vm):
        self.vm = vm

    # New in 3.4

    def LOAD_CLASSDEREF(self, count):
        """
        Much like LOAD_DEREF but first checks the locals dictionary before
        consulting the cell. This is used for loading free variables in class
        bodies.
        """
        self.vm.push(self.vm.frame.cells[i].get())

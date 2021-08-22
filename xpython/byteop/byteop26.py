# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6

Note: this is subclassed so later versions may use operations from here.
"""
from xdis import PYTHON_VERSION

if PYTHON_VERSION > 2.7:
    import importlib

from xpython.byteop.byteop import fmt_binary_op
from xpython.byteop.byteop25 import ByteOp25


class ByteOp26(ByteOp25):
    def __init__(self, vm):
        super(ByteOp26, self).__init__(vm)
        self.stack_fmt["IMPORT_NAME"] = fmt_binary_op

    # Right now 2.6 is largely the same as 2.5 here. How nice!

    def IMPORT_NAME(self, name):
        """
        Imports the module co_names[namei]. TOS and TOS1 are popped and
        provide the fromlist and level arguments of __import__().  The
        module object is pushed onto the stack.  The current namespace
        is not affected: for a proper import statement, a subsequent
        STORE_FAST instruction modifies the namespace.

        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        level, fromlist = self.vm.popn(2)
        frame = self.vm.frame

        if PYTHON_VERSION > 2.7:
            self.vm.push(
                importlib.__import__(
                    name, frame.f_globals, frame.f_locals, fromlist, level
                )
            )
        else:
            self.vm.push(
                __import__(name, frame.f_globals, frame.f_locals, fromlist, level)
            )

# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6

Note: this is subclassed so later versions may use operations from here.
"""
from xpython.byteop.byteop25 import ByteOp25

class ByteOp26(ByteOp25):
    def __init__(self, vm):
        super(ByteOp26, self).__init__(vm)

    # Right now 2.6 is largely the same as 2.5 here. How nice!

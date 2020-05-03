# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6
"""
from __future__ import print_function, division

from xpython.byteop.byteop25 import ByteOp25

class ByteOp26(ByteOp25):
    def __init__(self, vm, version=2.6):
        self.vm = vm
        self.version = version

    # Right now 2.6 is largely the same as 2.5 here. How nice!

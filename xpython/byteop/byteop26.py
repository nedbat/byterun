# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6
"""
from __future__ import print_function, division

from xpython.byteop.byteop25 import ByteOp25

import six
import sys
import operator
from xpython.pyobj import Function

class ByteOp26(ByteOp25):
    def __init__(self, vm):
        self.vm = vm
        self.version = 2.6

    # Right now 2.6 is largely the same as 2.5 here. How nice!

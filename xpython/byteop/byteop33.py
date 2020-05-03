# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.3
"""
from __future__ import print_function, division

from xpython.byteop.byteop32 import ByteOp32

class ByteOp33(ByteOp32):
    def __init__(self, vm, version=3.3):
        self.vm = vm
        self.version = version

    # Right now 3.3 is largely the same as 3.2 here. How nice!

if __name__ == "__main__":
    x = ByteOp33(None)

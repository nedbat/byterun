"""Byte Interpreter operations for Python 3.3
"""
from __future__ import print_function, division


from xpython.byteop.byteop27 import ByteOp27
from xpython.byteop.byteop26 import ByteOp26

# FIXME: investigate does "del" removing and attribute here
# have an effect on what another module sees as ByteOp27's attributes?

# Gone since 3.0
del ByteOp26.PRINT_EXPR
del ByteOp26.PRINT_ITEM
del ByteOp26.PRINT_ITEM_TO
del ByteOp26.PRINT_NEWLINE
del ByteOp26.PRINT_NEWLINE_TO
del ByteOp26.BUILD_CLASS
del ByteOp26.EXEC_STMT
# Gone since 3.2
del ByteOp26.DUP_TOPX


class ByteOp33(ByteOp27):
    def __init__(self, vm):
        self.vm = vm

    # Order of function here is the same as in:
    # https://docs.python.org/3.3/library/dis.html#python-bytecode-instructions

    # Note these are only the functions that aren't in the parent class
    # here, Python 2.7

    def DUP_TOP_TWO(self):
        """Duplicates the reference on top of the stack."""
        a, b = self.vm.popn(2)
        self.vm.push(a, b, a, b)

    def LOAD_BUILD_CLASS(self):
        """Pushes builtins.__build_class__() onto the stack. It is later called by CALL_FUNCTION to construct a class."""
        self.vm.push(__build_class__)

    # Is gone in 3.4
    def STORE_LOCALS(self):
        """Pops TOS from the stack and stores it as the current frame s f_locals. This is used in class construction."""
        self.vm.frame.f_locals = self.vm.pop()


if __name__ == "__main__":
    x = ByteOp33(None)

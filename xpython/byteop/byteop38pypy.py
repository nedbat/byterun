"""Bytecode Interpreter operations for PyPy 3.8
"""
from xpython.byteop.byteop37pypy import ByteOp37PyPy
from xpython.byteop.byteop38 import ByteOp38
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp38PyPy(ByteOp38, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp38PyPy, self).__init__(vm)
        self.version = "3.8.12 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"
        self.is_pypy = True

    # Python 3.8 removes SETUP_EXCEPT, but PyPy 3.8 still has it
    def SETUP_EXCEPT(self, jump_offset):
        """
        Pushes a try block from a try-except clause onto the block
        stack. delta points to the first except block.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """

        self.vm.push_block("setup-except", jump_offset)

    CALL_METHOD_KW = ByteOp37PyPy.CALL_METHOD_KW

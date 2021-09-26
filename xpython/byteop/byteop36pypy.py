"""Bytecode Interpreter operations for PyPy 3.6
"""
from __future__ import print_function, division

from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop36 import ByteOp35
from xpython.byteop.byteop36 import ByteOp36
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp36PyPy(ByteOp36, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp36PyPy, self).__init__(vm)

        # Fake up version information not already faked in super.
        self.version = "3.6.9 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

    # PyPy 3.6 BUILD_MAP_UNPACK_WITH_CALL follows older 3.5 convention, not current
    # 3.6 convention
    BUILD_MAP_UNPACK_WITH_CALL = ByteOp35.BUILD_MAP_UNPACK_WITH_CALL

    # PyPy 3.6 CALL_FUNCTION_KW follows older Python 2.4 convention, not current
    # changed 3.6 convention
    CALL_FUNCTION_KW = ByteOp24.CALL_FUNCTION_KW

    # FIXME: the below two functions might not be fully correct.
    # Look at bytecode-pypy3.6/test_comprehensions.pyc
    def BUILD_LIST_FROM_ARG(self, _):
        """
        """
        self.vm.push(list(self.vm.pop()))

    # In contrast to CPython, PyPy FOR_ITER needs to be able to deal with lists as well as generators.
    def FOR_ITER(self, jump_offset):
        """
        TOS is an iterator. Call its next() method. If this yields a new
        value, push it on the stack (leaving the iterator below
        it). If the iterator indicates it is exhausted TOS is popped,
        and the bytecode counter is incremented by delta.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """

        iterobj = self.vm.top()
        if not hasattr(iterobj, "next"):
            iterobj = (x for x in iterobj)
        try:
            v = next(iterobj)
            self.vm.push(v)
        except StopIteration:
            self.vm.pop()
            self.vm.jump(jump_offset)

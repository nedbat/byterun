"""Bytecode Interpreter operations for PyPy 3.6
"""

from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop35 import ByteOp35
from xpython.byteop.byteop36 import ByteOp36
from xpython.byteop.byteoppypy import ByteOpPyPy


class ByteOp36PyPy(ByteOp36, ByteOpPyPy):
    def __init__(self, vm):
        super(ByteOp36PyPy, self).__init__(vm)
        self.is_pypy = True

        # Fake up version information not already faked in super.
        self.version = "3.6.9 (x-python, Oct 27 1955, 00:00:00)\n[PyPy with x-python]"

    # Python 3.6 changes the semantics of the below opcodes.
    # However PyPy 3.6 uses the previous semantics, which we can pull
    # from older Python versions
    CALL_FUNCTION_KW = ByteOp24.CALL_FUNCTION_KW
    BUILD_MAP_UNPACK_WITH_CALL = ByteOp35.BUILD_MAP_UNPACK_WITH_CALL

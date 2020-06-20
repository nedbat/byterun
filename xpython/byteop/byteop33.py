# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.3
"""
from __future__ import print_function, division

from xpython.byteop.byteop32 import ByteOp32
from xpython.pyobj import Generator


class ByteOp33(ByteOp32):
    def __init__(self, vm):
        super(ByteOp33, self).__init__(vm)

    # Right now 3.3 is largely the same as 3.2 here. How nice!

    def YIELD_FROM(self):
        """
        Pops TOS and delegates to it as a subiterator from a generator.
        """
        u = self.vm.pop()
        x = self.vm.top()

        try:
            if not isinstance(x, Generator) or u is None:
                # Call next on iterators.
                retval = next(x)
            else:
                retval = x.send(u)
            self.vm.return_value = retval
        except StopIteration as e:
            self.vm.pop()
            self.vm.push(e.value)
        else:
            # FIXME: The code has the effect of rerunning the last instruction.
            # I'm not sure if or why it is correct.
            if self.vm.version >= 3.6:
                self.vm.jump(self.vm.frame.f_lasti - 2)
            else:
                self.vm.jump(self.vm.frame.f_lasti - 1)
            return "yield"

    # Python 3.3 docs describe a 3.4 MAKE_FUNCTION but seem to follow pre-3.3
    # conventions (which go back to Python 2.x days).
    # def MAKE_FUNCTION(self, argc):

if __name__ == "__main__":
    x = ByteOp33(None)

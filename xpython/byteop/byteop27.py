"""Bytecode Interpreter operations for Python 2.7
"""
from __future__ import print_function, division

from xdis import IS_PYPY
from xpython.byteop.byteop25 import ByteOp25
from xpython.byteop.byteop26 import ByteOp26

# Gone since 2.6
del ByteOp25.JUMP_IF_FALSE
del ByteOp25.JUMP_IF_TRUE

class ByteOp27(ByteOp26):
    def __init__(self, vm):
        super(ByteOp27, self).__init__(vm)


    # New in 2.7

    # Note SET_ADD and MAP_ADD don't seem to be documented in
    # the 2.7 docs although the first appear there.
    # The docstring for these below is taken from 3.1 docs.
    # (3.0 doesn't have have MAP, although it has SET
    # which is exactly what is below.)
    def SET_ADD(self, count):
        """Calls set.add(TOS1[-i], TOS). Used to implement set
        comprehensions.
        """
        val = self.vm.pop()
        the_set = self.vm.peek(count)
        the_set.add(val)

    def MAP_ADD(self, count):
        """
        Calls dict.setitem(TOS1[-i], TOS, TOS1). Used to implement dict
        comprehensions.
        """
        val, key = self.vm.popn(2)
        the_map = self.vm.peek(count)
        the_map[key] = val

    def BUILD_SET(self, count):
        """Works as BUILD_TUPLE, but creates a set. New in version 2.7"""
        elts = self.vm.popn(count)
        self.vm.push(set(elts))

    def JUMP_FORWARD(self, delta):
        """Increments bytecode counter by delta."""
        self.vm.jump(delta)

    def POP_JUMP_IF_TRUE(self, target):
        """If TOS is true, sets the bytecode counter to target. TOS is popped."""
        val = self.vm.pop()
        if val:
            self.vm.jump(target)

    def POP_JUMP_IF_FALSE(self, target):
        """If TOS is false, sets the bytecode counter to target. TOS is popped."""
        val = self.vm.pop()
        if not val:
            self.vm.jump(target)

    def JUMP_IF_TRUE_OR_POP(self, target):
        """
        If TOS is true, sets the bytecode counter to target and leaves TOS
        on the stack. Otherwise (TOS is false), TOS is popped.
        """
        val = self.vm.top()
        if val:
            self.vm.jump(target)
        else:
            self.vm.pop()

    def JUMP_IF_FALSE_OR_POP(self, target):
        """
        If TOS is false, sets the bytecode counter to target and leaves TOS
        on the stack. Otherwise (TOS is true), TOS is popped.
        """
        val = self.vm.top()
        if not val:
            self.vm.jump(target)
        else:
            self.vm.pop()

    def JUMP_ABSOLUTE(self, target):
        self.vm.jump(target)

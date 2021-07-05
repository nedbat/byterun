# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 3.8
"""
from __future__ import print_function, division

from xpython.byteop.byteop37 import ByteOp37
from xpython.byteop.byteop24 import ByteOp24


# Gone in 3.8
del ByteOp24.BREAK_LOOP
del ByteOp24.CONTINUE_LOOP
del ByteOp24.SETUP_LOOP
del ByteOp24.SETUP_EXCEPT


class ByteOp38(ByteOp37):
    def __init__(self, vm):
        super(ByteOp38, self).__init__(vm)

    # Changed in 3.8...

    # New in 3.8

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.8/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    def BEGIN_FINALLY(self):
        """Pushes NULL onto the stack for using it in END_FINALLY, POP_FINALLY, WITH_CLEANUP_START and WITH_CLEANUP_FINISH. Starts the finally block."""
        raise self.vm.PyVMError("BEGIN_FINALLY not implemented yet")

    def END_ASYNC_FOR(self):
        """Terminates an `async for1 loop. Handles an exception raised when
        awaiting a next item. If TOS is StopAsyncIteration pop 7 values from
        the stack and restore the exception state using the second three of
        them. Otherwise re-raise the exception using the three values from the
        stack. An exception handler block is removed from the block stack."""

        raise self.vm.PyVMError("END_ASYNC_FOR not implemented yet")

    def END_FINALLY(self):
        """Terminates a finally clause. The interpreter recalls whether the
        exception has to be re-raised or execution has to be continued
        depending on the value of TOS.

        * If TOS is NULL (pushed by BEGIN_FINALLY) continue from the next instruction.
          TOS is popped.

        * If TOS is an integer (pushed by CALL_FINALLY), sets the bytecode counter to TOS.
          TOS is popped.

        * If TOS is an exception type (pushed when an exception has
          been raised) 6 values are popped from the stack, the first
          three popped values are used to re-raise the exception and
          the last three popped values are used to restore the
          exception state. An exception handler block is removed from
          the block stack.

        """
        raise self.vm.PyVMError("END_FINALLY not implemented yet")

    def CALL_FINALLY(self, delta):
        """Pushes the address of the next instruction onto the stack and
        increments bytecode counter by delta. Used for calling the
        finally block as a “subroutine
        """

        raise self.vm.PyVMError("CALL_FINALLY not implemented yet")

    def POP_FINALLY(self):
        """Cleans up the value stack and the block stack. If preserve_tos is
        not 0 TOS first is popped from the stack and pushed on the stack after
        performing other stack operations:

        * If TOS is NULL or an integer (pushed by BEGIN_FINALLY or CALL_FINALLY) it is popped from the stack.
        * If TOS is an exception type (pushed when an exception has been raised) 6 values are popped from the
          stack, the last three popped values are used to restore the exception state. An exception handler
          block is removed from the block stack.

        It is similar to END_FINALLY, but doesn’t change the bytecode
        counter nor raise an exception. Used for implementing break,
        continue and return in the finally block.

        """
        raise self.vm.PyVMError("POP not implemented yet")

    # Changed from 2.4: Map value is TOS and map key is TOS1. Before, those were reversed.
    def MAP_ADD(self, count):
        """Calls dict.setitem(TOS1[-count], TOS1, TOS). Used to implement dict
        comprehensions.

        For all of the SET_ADD, LIST_APPEND and MAP_ADD instructions,
        while the added value or key/value pair is popped off, the
        container object remains on the stack so that it is available
        for further iterations of the loop.
        """
        # FIXME: the below seems fishy.
        key, val = self.vm.popn(2)
        the_map = self.vm.peek(count)
        the_map[key] = val

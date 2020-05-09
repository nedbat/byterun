"""Bytecode Interpreter operations for Python 3.7
"""
from __future__ import print_function, division

import types
from xpython.byteop.byteop36 import ByteOp36

# Gone in 3.7
del ByteOp36.STORE_ANNOTATION
# del ByteOp36.WITH_CLEANUP_START
# del ByteOp36.WITH_CLEANUP_FINISH
# del ByteOp36.END_FINALLY
# del ByteOp36.POP_EXCEPT
# del ByteOp36.SETUP_WITH
# del ByteOp36.SETUP_ASYNC_WITH

class ByteOp37(ByteOp36):
    def __init__(self, vm):
        super(ByteOp37, self).__init__(vm)

    # Changed in 3.7

    # WITH_CLEANUP_START
    # WITH_CLEANUP_FINISH
    # END_FINALLY
    # POP_EXCEPT
    # SETUP_WITH
    # SETUP_ASYNC_WITH

    # New in 3.7

    ##############################################################################
    # Order of function here is the same as in:
    # https://docs.python.org/3.7/library/dis.htmls#python-bytecode-instructions
    #
    # A note about parameter names. Generally they are the same as
    # what is described above, however there are some slight changes:
    #
    # * when a parameter name is `namei` (an int), it appears as
    #   `name` (a str) below because the lookup on co_names[namei] has
    #   already been performed in parse_byte_and_args().
    ##############################################################################

    def LOAD_METHOD(self, name):
        """Loads a method named co_names[namei] from the TOS object. TOS is
        popped. This bytecode distinguishes two cases: if TOS has a
        method with the correct name, the bytecode pushes the unbound
        method and TOS. TOS will be used as the first argument (self)
        by CALL_METHOD when calling the unbound method. Otherwise,
        NULL and the object return by the attribute lookup are pushed.

        rocky: In our implementation in Python we don't have NULL: all
        stack entries have *some* value. So instead we'll push another
        item: the status. Also, instead of pushing the unbound method
        and self, we will pass the bound method, since that is what we
        have here. So TOS (self) is not pushed back onto the stack.
        """
        TOS = self.vm.pop()
        if hasattr(TOS, name):
            # FIXME: check that gettr(TO, name) is a method
            self.vm.push(getattr(TOS, name))
            self.vm.push("LOAD_METHOD lookup success")
        else:
            self.vm.push("fill in attribute method lookup")
            self.vm.push(None)

    def CALL_METHOD(self, count):
        """Calls a method. argc is the number of positional
        arguments. Keyword arguments are not supported. This opcode is
        designed to be used with LOAD_METHOD. Positional arguments are
        on top of the stack. Below them, the two items described in
        LOAD_METHOD are on the stack (either self and an unbound
        method object or NULL and an arbitrary callable). All of them
        are popped and the return value is pushed.

        rocky: In our setting, before "self" we have an additional
        item which is the status of the LOAD_METHOD. There is no way
        in Python to represent a value outside of a Python value which
        you can do in C, and is in effect what NULL is.
        """
        posargs = self.vm.popn(count)
        is_success = self.vm.pop()
        if is_success:
            func = self.vm.pop()
            self.call_function_with_args_resolved(func, posargs, {})
        else:
            # FIXME: do something else
            raise self.vm.PyVMError("CALL_METHOD not implemented yet")

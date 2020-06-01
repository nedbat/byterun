# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.5

Note: this is subclassed. Later versions use operations from here.
"""
from __future__ import print_function, division

from xpython.byteop.byteop24 import ByteOp24

class ByteOp25(ByteOp24):
    def __init__(self, vm):
        super(ByteOp25, self).__init__(vm)

    # New in Python 2.5 but changes in 3.3.
    def WITH_CLEANUP(self):
        """Cleans up the stack when a "with" statement block exits. On top of
        the stack are 1 3 values indicating how/why the finally clause
        was entered:

        * TOP = None
        * (TOP, SECOND) = (WHY_{RETURN,CONTINUE}), retval
        * TOP = WHY_*; no retval below it
        * (TOP, SECOND, THIRD) = exc_info()

        Under them is EXIT, the context manager s __exit__() bound method.

        In the last case, EXIT(TOP, SECOND, THIRD) is called,
        otherwise EXIT(None, None, None).

        EXIT is removed from the stack, leaving the values above it in
        the same order. In addition, if the stack represents an
        exception, and the function call returns a  true  value, this
        information is  zapped , to prevent END_FINALLY from
        re-raising the exception. (But non-local gotos should still be
        resumed.)

        All of the following opcodes expect arguments. An argument is
        two bytes, with the more significant byte last.
        """
        # The code here does some weird stack manipulation: the __exit__ function
        # is buried in the stack, and where depends on what's on top of it.
        # Pull out the exit function, and leave the rest in place.
        # In Python 3.x this is fixed up so that the __exit__ funciton os TOS
        v = w = None
        u = self.vm.top()
        if u is None:
            exit_func = self.vm.pop(1)
        elif isinstance(u, str):
            if u in ("return", "continue"):
                exit_func = self.vm.pop(2)
            else:
                exit_func = self.vm.pop(1)
            u = None
        elif issubclass(u, BaseException):
            w, v, u = self.vm.popn(3)
            exit_func = self.vm.pop()
            self.vm.push(w, v, u)
        else:  # pragma: no cover
            raise self.vm.PyVMError("Confused WITH_CLEANUP")
        exit_ret = exit_func(u, v, w)
        err = (u is not None) and bool(exit_ret)
        if err:
            # An error occurred, and was suppressed
            self.vm.popn(3)
            self.vm.push(None)

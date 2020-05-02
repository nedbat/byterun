# -*- coding: utf-8 -*-
"""Byte Interpreter operations for Python 3.3
"""
from __future__ import print_function, division

from xpython.pyobj import Function
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
        self.version = 3.3

    # Changed from 2.7
    # 3.3 has kwdefaults that aren't allowed in 2.7
    def MAKE_FUNCTION(self, argc):
        """
        Pushes a new function object on the stack. From bottom to top, the consumed stack must consist of:

        * argc & 0xFF default argument objects in positional order
        * (argc >> 8) & 0xFF pairs of name and default argument, with the name just below the object on the stack, for keyword-only parameters
        * (argc >> 16) & 0x7FFF parameter annotation objects
        * a tuple listing the parameter names for the annotations (only if there are ony annotation objects)
        * the code associated with the function (at TOS1)
        * the qualified name of the function (at TOS)
        """
        rest, default_count = divmod(argc, 256)
        annotate_count, kw_default_count = divmod(rest, 256)

        name = self.vm.pop()
        code = self.vm.pop()
        if annotate_count:
            annotate_names = self.vm.pop()
            annotate_objects = self.vm.popn(annotate_count)
            n = len(annotate_names)
            assert n == len(annotate_objects)
            annotations = {annotate_names[i]:annotate_objects[i] for i in range(n)}
        else:
            annotations = {}

        if kw_default_count:
            kw_default_pairs = self.vm.popn(2 * kw_default_count)
            kwdefaults = dict(kw_default_pairs[i:i+2] for i in range(0, len(kw_default_pairs), 2))
        else:
            kwdefaults = {}

        if default_count:
            defaults = self.vm.popn(default_count)
        else:
            defaults = tuple()

        globs = self.vm.frame.f_globals

        fn = Function(name, code, globs, defaults,
                      closure=None,
                      vm = self.vm,
                      kwdefaults=kwdefaults,
                      annotations=annotations)
        fn.version = self.version
        self.vm.push(fn)

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

    # This opcode is replaced by WITH_CLEANUP_START and WITH_CLEANUP_FINISH in in 3.5
    def WITH_CLEANUP(self):
        """Cleans up the stack when a `with` statement block exits. TOS is the
        context manager's `__exit__()` bound method.

        Below TOS are 1–3 values indicating how/why the finally clause
        was entered:

        * SECOND = None
        * (SECOND, THIRD) = (WHY_{RETURN,CONTINUE}), retval
        * SECOND = WHY_*; no retval below it
        * (SECOND, THIRD, FOURTH) = exc_info()

        In the last case, EXIT(SECOND, THIRD, FOURTH) is called,
        otherwise TOS(None, None, None). In addition, TOS is removed from the stack.

        If the stack represents an exception, and the function call
        returns a ‘true’ value, this information is “zapped” and
        replaced with a single WHY_SILENCED to prevent END_FINALLY
        from re-raising the exception. (But non-local gotos will still
        be resumed.)
        """
        # FIXME rocky: the code is derived from byterun where it had to handle
        # both 2.7 and 3.3.
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
            tp, exc, tb = self.vm.popn(3)
            exit_func = self.vm.pop()
            self.vm.push(tp, exc, tb)
            self.vm.push(None)
            self.vm.push(w, v, u)
            block = self.vm.pop_block()
            assert block.type == "except-handler"
            self.vm.push_block(block.type, block.handler, block.level - 1)
        else:  # pragma: no cover
            raise self.VirtualMachineError("Confused WITH_CLEANUP")
        exit_ret = exit_func(u, v, w)
        err = (u is not None) and bool(exit_ret)
        if err:
            # An error occurred, and was suppressed
                self.vm.push("silenced")

    # Note: this is gone in 3.4
    def STORE_LOCALS(self):
        """Pops TOS from the stack and stores it as the current frame s f_locals. This is used in class construction."""
        self.vm.frame.f_locals = self.vm.pop()


if __name__ == "__main__":
    x = ByteOp33(None)

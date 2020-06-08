"""Bytecode Interpreter operations for Python 2.7
"""
from __future__ import print_function, division

import inspect
import types
from xdis import PYTHON_VERSION
from xpython.byteop.byteop24 import ByteOp24
from xpython.byteop.byteop26 import ByteOp26

# Gone since 2.6
del ByteOp24.JUMP_IF_FALSE
del ByteOp24.JUMP_IF_TRUE

def fmt_set_add(vm, arg, repr=repr):
    return " set.add(%s, %s)" % (repr(vm.peek(arg)), repr(vm.top()))

def fmt_map_add(vm, arg, repr=repr):
    return " dict.setitem(%s, %s, %s)" % (repr(vm.peek(arg)), repr(vm.top()), repr(vm.peek(2)))

class ByteOp27(ByteOp26):
    def __init__(self, vm):
        super(ByteOp27, self).__init__(vm)
        self.stack_fmt["SET_ADD"] = fmt_set_add
        self.stack_fmt["MAP_ADD"] = fmt_map_add

    def convert_method_native_func(self, frame, method):
        """If a method's function is a native functions, converted it to the
        corresponding PyVM Method so that we can interpret it.
        """
        if not self.method_func_access:
            for func_attr in ("__func__", "im_func"):
                if hasattr(method, func_attr):
                    # Save attribute access name, so we don't
                    # have to compute this again.
                    self.method_func_access = func_attr
                    break
                pass
            else:
                raise self.vm.PyVMError("Can't find method function attribute; tried '__func__' and '_im_func'")
            pass

        try:
            func = getattr(method, self.method_func_access)
        except:
            func = method

        if inspect.isfunction(func):
            func = self.convert_native_to_Function(self.vm.frame, func)
            method = types.MethodType(func, method.__self__)
        return method

    # New in 2.7

    # Note SET_ADD and MAP_ADD don't seem to be documented in
    # the 2.7 docs although the first appear there.
    # The docstring for these below is taken from 3.1 docs.
    # (3.0 doesn't have have MAP, although it has SET
    # which is what is below.)

    # The descripitons of these is weird becase values are
    # peeked and not popped. Probably has something to do with
    # the way comprehensions work.
    def SET_ADD(self, count):
        """Calls set.add(TOS1[-count], TOS). Used to implement set
        comprehensions.
        """
        val = self.vm.pop()
        the_set = self.vm.peek(count)
        the_set.add(val)

    def MAP_ADD(self, count):
        """
        Calls dict.setitem(TOS1[-count], TOS, TOS1). Used to implement dict
        comprehensions.
        """
        # FIXME: the below seems fishy.
        val, key = self.vm.popn(2)
        the_map = self.vm.peek(count)
        the_map[key] = val

    # Note gone in 3.0 and 3.1, but appears again in 3.2
    def SETUP_WITH(self, delta):
        """
        This opcode performs several operations before a with block
        starts. First, it loads __exit__() from the context manager
        and pushes it onto the stack for later use by
        WITH_CLEANUP. Then, __enter__() is called, and a finally block
        pointing to delta is pushed. Finally, the result of calling
        the enter method is pushed onto the stack. The next opcode
        will either ignore it (POP_TOP), or store it in (a)
        variable(s) (STORE_FAST, STORE_NAME, or UNPACK_SEQUENCE).
        """
        context_manager = self.vm.pop()

        # Make sure __enter__ and __exit__ functions in context_manager are
        # converted to our Function type so we can interpret them.
        # Note though that built-in functions can't be traced.
        if self.version == PYTHON_VERSION and not inspect.isbuiltin(context_manager.__exit__):
            try:
                exit_method = self.convert_method_native_func(self.vm.frame, context_manager.__exit__)
            except:
                exit_method = context_manager.__exit__
        else:
            exit_method = context_manager.__exit__
        self.vm.push(exit_method)
        if self.version == PYTHON_VERSION and not inspect.isbuiltin(context_manager.__enter__):
            self.convert_method_native_func(self.vm.frame, context_manager.__enter__)
        finally_block = context_manager.__enter__()
        if self.version < 3.0:
            self.vm.push_block("with", delta)
        else:
            self.vm.push_block("finally", delta)
        self.vm.push(finally_block)

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

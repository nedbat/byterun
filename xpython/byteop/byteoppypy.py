"""Bytecode Interpreter operations for PyPy in general (all versions)

Specific PyPy versions i.e. PyPy 2.7, 3.2, 3.5-3.7 inherit this.
"""
from __future__ import print_function, division


class ByteOpPyPy(object):
    def call_method(self, argc, var_args, keyword_args):
        named_args = {}
        len_kw, len_pos = divmod(argc, 256)
        for i in range(len_kw):
            key, val = self.vm.popn(2)
            named_args[key] = val
        named_args.update(keyword_args)
        pos_args = self.vm.popn(len_pos)
        pos_args.extend(var_args)

        im_self = self.vm.pop()
        if im_self is not None:
            pos_args.insert(0, im_self)
        im_func = self.vm.pop()
        return self.call_function_with_args_resolved(im_func, pos_args, named_args)

    def JUMP_IF_NOT_DEBUG(self, jump_offset):
        """
        For now, same as JUMP_ABSOLUTE.
        """
        self.vm.jump(jump_offset)

    # See https://doc.pypy.org/en/latest/interpreter-optimizations.html#lookup-method-call-method
    def LOOKUP_METHOD(self, name):
        """LOOKUP_METHOD contains exactly the same attribute lookup logic as
        LOAD_ATTR - thus fully preserving semantics - but pushes two
        values onto the stack instead of one. These two values are an
         inlined  version of the bound method object: the im_func and
        im_self, i.e. respectively the underlying Python function
        object and a reference to obj. This is only possible when the
        attribute actually refers to a function object from the class;
        when this is not the case, LOOKUP_METHOD still pushes two
        values, but one (im_func) is simply the regular result that
        LOAD_ATTR would have returned, and the other (im_self) is an
        interpreter-level None placeholder.

        Replaces TOS with getattr(TOS, co_names[namei]).
        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        obj = self.vm.pop()
        im_func = getattr(obj, name)
        # FIXME: start here: not quite right
        im_self = im_func.self if hasattr(im_func, "self") else None
        self.vm.push(im_func)
        self.vm.push(im_self)

    def CALL_METHOD(self, argc):
        """The CALL_METHOD N bytecode emulates a bound method call by
        inspecting the im_self entry in the stack below the N
        arguments: if it is not None, then it is considered to be an
        additional first argument in the call to the im_func object
        from the stack.

        Calls a callable object.
        The low byte of argc indicates the number of positional
        arguments, the high byte the number of keyword arguments.
        """
        return self.call_method(argc, [], {})

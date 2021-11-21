"""Bytecode Interpreter operations for PyPy in general (all versions)

Specific PyPy versions i.e. PyPy 2.7, 3.2, 3.5-3.7 inherit this.
"""
import inspect


class ByteOpPyPy(object):
    def BUILD_LIST_FROM_ARG(self, count: int):
        """Builds a list containing TOS.
        Is equivalint to BUILD_LIST(0) followed by ROT_TWO
        """
        self.BUILD_LIST(count)
        self.ROT_TWO()

    def JUMP_IF_NOT_DEBUG(self, jump_offset):
        """
        For now, same as JUMP_ABSOLUTE.
        """
        self.vm.jump(jump_offset)

    # For Python 3.7 this is not correct
    def LOOKUP_METHOD(self, name):
        """
        For now, we'll assume this is the same as LOAD_ATTR:

        Replaces TOS with getattr(TOS, co_names[namei]).
        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        obj = self.vm.pop()
        val = getattr(obj, name)
        self.vm.push(val)
        if self.version_info[:2] >= (3, 7):
            if inspect.isfunction(val) or inspect.isbuiltin(val):
                self.vm.push("LOAD_METHOD lookup success")
            else:
                self.vm.push("fill in attribute method lookup")

    def CALL_METHOD(self, argc):
        """
        For now, we'll assume this is like CALL_FUNCTION:

        Calls a callable object.
        The low byte of argc indicates the number of positional
        arguments, the high byte the number of keyword arguments.
        ...
        """
        return self.call_function(argc, [], {})

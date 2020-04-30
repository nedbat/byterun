"""Byte Interpreter operations for Python 2.7
"""
from __future__ import print_function, division

import sys

class ByteOp27():
    def __init__(self, vm):
        self.vm = vm

    # Order of function here is the same as in:
    # https://docs.python.org/2.7/library/dis.html#python-bytecode-instructions

    def NOP(self):
        "Do nothing code. Used as a placeholder by the bytecode optimizer."
        pass

    ## Stack manipulation

    def POP_TOP(self):
        "Removes the top-of-stack (TOS) item."
        self.vm.pop()

    def ROT_TWO(self):
        "Swaps the two top-most stack items."
        a, b = self.vm.popn(2)
        self.vm.push(b, a)

    def ROT_THREE(self):
        "Lifts second and third stack item one position up, moves top down to position three."
        a, b, c = self.vm.popn(3)
        self.vm.push(c, a, b)

    def ROT_FOUR(self):
        "Lifts second, third and forth stack item one position up, moves top down to position four."
        a, b, c, d = self.vm.popn(4)
        self.vm.push(d, a, b, c)

    def DUP_TOP(self):
        """Duplicates the reference on top of the stack."""
        self.vm.push(self.vm.top())

    # Unary operators are handled elsewhere

    def GET_ITER(self):
        """Implements TOS = iter(TOS)."""
        self.vm.push(iter(self.vm.pop()))

    # Binary operators are handled elsewhere
    # Inplace operators are handled elsewhere
    # Slice operators are handled elsewhere

    def STORE_SUBSCR(self):
        """Implements TOS1[TOS] = TOS2."""
        val, obj, subscr = self.vm.popn(3)
        obj[subscr] = val

    def DELETE_SUBSCR(self):
        """Implements del TOS1[TOS]."""
        obj, subscr = self.vm.popn(2)
        del obj[subscr]

    ## Printing

    # Only used in the interactive interpreter, not in modules.
    def PRINT_EXPR(self):
        print(self.vm.pop())

    def PRINT_ITEM(self):
        item = self.vm.pop()
        self.print_item(item)

    def PRINT_ITEM_TO(self):
        to = self.vm.pop()
        item = self.vm.pop()
        self.print_item(item, to)

    def PRINT_NEWLINE(self):
        self.print_newline()

    def PRINT_NEWLINE_TO(self):
        to = self.vm.pop()
        self.print_newline(to)

    def print_item(self, item, to=None):
        if to is None:
            to = sys.stdout
        if to.softspace:
            print(" ", end="", file=to)
            to.softspace = 0
        print(item, end="", file=to)
        if isinstance(item, str):
            if (not item) or (not item[-1].isspace()) or (item[-1] == " "):
                to.softspace = 1
        else:
            to.softspace = 1

    def print_newline(self, to=None):
        if to is None:
            to = sys.stdout
        print("", file=to)
        to.softspace = 0

    def LOAD_CONST(self, const):
        """Pushes co_consts[consti] onto the stack."""
        self.vm.push(const)

    def LOAD_NAME(self, name):
        frame = self.vm.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.vm.push(val)

    def DUP_TOPX(self, count):
        """Duplicate count items, keeping them in the same order. Due to implementation limits, count should be between 1 and 5 inclusive."""
        items = self.vm.popn(count)
        for i in [1, 2]:
            self.vm.push(*items)

    def BUILD_CLASS(self):
        """Creates a new class object. TOS is the methods dictionary, TOS1 the tuple of the names of the base classes, and TOS2 the class name."""
        name, bases, methods = self.vm.popn(3)
        self.vm.push(type(name, bases, methods))

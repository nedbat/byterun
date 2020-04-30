"""Byte Interpreter operations for Python 2.7
"""
from __future__ import print_function, division

import sys
import operator


class ByteOp27:
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
        """Pushes the value associated with co_names[namei] onto the stack."""
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

    ## Building

    def BUILD_TUPLE(self, count):
        """Creates a tuple consuming count items from the stack, and pushes the resulting tuple onto the stack."""
        elts = self.vm.popn(count)
        self.vm.push(tuple(elts))

    def BUILD_LIST(self, count):
        """Works as BUILD_TUPLE, but creates a list."""
        elts = self.vm.popn(count)
        self.vm.push(elts)

    def BUILD_SET(self, count):
        """Works as BUILD_TUPLE, but creates a set. New in version 2.7"""
        elts = self.vm.popn(count)
        self.vm.push(set(elts))

    def BUILD_MAP(self, size):
        """Pushes a new dictionary object onto the stack. The dictionary is pre-sized to hold count entries."""
        # "size" is ignored; In contrast to C, in Python, the default dictionary type has no notion of allocation size.
        self.vm.push({})

    ## end BUILD_ operators

    def LOAD_ATTR(self, namei):
        """Replaces TOS with getattr(TOS, co_names[namei])."""
        obj = self.vm.pop()
        val = getattr(obj, namei)
        self.vm.push(val)

    ## Commparisons

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
        lambda x, y: x in y,
        lambda x, y: x not in y,
        lambda x, y: x is y,
        lambda x, y: x is not y,
        lambda x, y: issubclass(x, Exception) and issubclass(x, y),
    ]

    def COMPARE_OP(self, opname):
        """Performs a Boolean operation. The operation name can be found in cmp_op[opname]."""
        x, y = self.vm.popn(2)
        self.vm.push(self.COMPARE_OPERATORS[opname](x, y))

    ## Imports

    def IMPORT_NAME(self, namei):
        """
        Imports the module co_names[namei]. TOS and TOS1 are popped and
        provide the fromlist and level arguments of __import__().  The
        module object is pushed onto the stack.  The current namespace
        is not affected: for a proper import statement, a subsequent
        STORE_FAST instruction modifies the namespace.
        """
        level, fromlist = self.vm.popn(2)
        frame = self.vm.frame
        self.vm.push(
            __import__(namei, frame.f_globals, frame.f_locals, fromlist, level)
        )

    def IMPORT_FROM(self, namei):
        """
        Loads the attribute co_names[namei] from the module found in TOS.
        The resulting object is pushed onto the stack, to be
        subsequently stored by a STORE_FAST instruction.

        """
        mod = self.vm.top()
        self.vm.push(getattr(mod, namei))

    ## Jumps

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

    ## end Jump section

    def FOR_ITER(self, delta):
        """
        TOS is an iterator. Call its next() method. If this yields a new
        value, push it on the stack (leaving the iterator below
        it). If the iterator indicates it is exhausted TOS is popped,
        and the bytecode counter is incremented by delta.
        """

        iterobj = self.vm.top()
        try:
            v = next(iterobj)
            self.vm.push(v)
        except StopIteration:
            self.vm.pop()
            self.vm.jump(delta)

    def LOAD_GLOBAL(self, name):
        """Loads the global named co_names[namei] onto the stack."""
        f = self.vm.frame
        if name in f.f_globals:
            val = f.f_globals[name]
        elif name in f.f_builtins:
            val = f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        self.vm.push(val)

    def SETUP_LOOP(self, delta):
        """
        Pushes a block for a loop onto the block stack. The block spans
        from the current instruction with a size of delta bytes.
        """
        self.vm.push_block("loop", delta)

    def SETUP_EXCEPT(self, delta):
        """
        Pushes a try block from a try-except clause onto the block
        stack. delta points to the first except block.
        """

        self.vm.push_block("setup-except", delta)

    def SETUP_FINALLY(self, delta):
        self.vm.push_block("finally", delta)

    def DUP_TOPX(self, count):
        """
        Duplicate count items, keeping them in the same order. Due to
        implementation limits, count should be between 1 and 5 inclusive.
        """
        items = self.vm.popn(count)
        for i in [1, 2]:
            self.vm.push(*items)

    def BUILD_CLASS(self):
        """
        Creates a new class object. TOS is the methods dictionary, TOS1 the
        tuple of the names of the base classes, and TOS2 the class name.
        """
        name, bases, methods = self.vm.popn(3)
        self.vm.push(type(name, bases, methods))

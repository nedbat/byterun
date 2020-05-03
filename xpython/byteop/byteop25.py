# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.5
"""
from __future__ import print_function, division

import six
import sys
import operator
from xpython.pyobj import Function

class ByteOp25():
    def __init__(self, vm, version=2.5):
        self.vm = vm
        self.version = version

    # Order of function here is the same as in:
    # https://docs.python.org/2.5/library/dis.html#python-bytecode-instructions

    def NOP(self):
        "Do nothing code. Used as a placeholder by the bytecode optimizer."
        pass

    # Stack manipulation

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

    # Printing

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

    def BREAK_LOOP(self):
        """Terminates a loop due to a break statement."""
        return "break"

    def CONTINUE_LOOP(self, dest):
        """
        Continues a loop due to a continue statement. target is the
        address to jump to (which should be a FOR_ITER instruction).
        """
        # This is a trick with the return value.
        # While unrolling blocks, continue and return both have to preserve
        # state as the finally blocks are executed.  For continue, it's
        # where to jump to, for return, it's the value to return.  It gets
        # pushed on the stack for both, so continue puts the jump destination
        # into return_value.
        self.vm.return_value = dest
        return "continue"

    def RETURN_VALUE(self):
        """Returns with TOS to the caller of the function.
        """
        self.vm.return_value = self.vm.pop()
        if self.vm.frame.generator:
            self.vm.frame.generator.finished = True
        return "return"

    def YIELD_VALUE(self):
        """
        Pops TOS and yields it from a generator.
        """
        self.vm.return_value = self.vm.pop()
        return "yield"

    def print_item(self, item, to=None):
        if to is None:
            to = sys.stdout

        # Python 2ish has file.sofspace whereas
        # Python 3ish doesn't. Here is the doc on softspace:

        # Boolean that indicates whether a space character needs to be
        # printed before another value when using the print
        # statement. Classes that are trying to simulate a file object
        # should also have a writable softspace attribute, which
        # should be initialized to zero. This will be automatic for
        # most classes implemented in Python (care may be needed for
        # objects that override attribute access); types implemented
        # in C will have to provide a writable softspace attribute.

        # Note This attribute is not used to control the print
        # statement, but to allow the implementation of print to keep
        # track of its internal state.
        if hasattr(to, "softspace") and to.softspace:
            print(" ", end="", file=to)
            to.softspace = 0
        print(item, end="", file=to)

        if hasattr(to, "softspace"):
            if isinstance(item, str):
                if (not item) or (not item[-1].isspace()) or (item[-1] == " "):
                    to.softspace = 1
            else:
                to.softspace = 1

    def print_newline(self, to=None):
        if to is None:
            to = sys.stdout
        print("", file=to)
        if hasattr(to, "softspace"):
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

    # Building

    def BUILD_TUPLE(self, count):
        """Creates a tuple consuming count items from the stack, and pushes
        the resulting tuple onto the stack.
        """
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
        """
        Pushes a new dictionary object onto the stack. The dictionary is
        pre-sized to hold count entries.
        """
        # "size" is ignored; In contrast to C, in Python, the default dictionary type has no
        # notion of allocation size.
        self.vm.push({})

    # end BUILD_ operators

    def LOAD_ATTR(self, name):
        """Replaces TOS with getattr(TOS, co_names[namei]).

        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        obj = self.vm.pop()
        val = getattr(obj, name)
        self.vm.push(val)

    # Commparisons

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

    # Imports

    def IMPORT_NAME(self, name):
        """
        Imports the module co_names[namei]. TOS and TOS1 are popped and
        provide the fromlist and level arguments of __import__().  The
        module object is pushed onto the stack.  The current namespace
        is not affected: for a proper import statement, a subsequent
        STORE_FAST instruction modifies the namespace.

        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        level, fromlist = self.vm.popn(2)
        frame = self.vm.frame
        self.vm.push(
            __import__(name, frame.f_globals, frame.f_locals, fromlist, level)
        )

    def IMPORT_FROM(self, name):
        """
        Loads the attribute co_names[namei] from the module found in TOS.
        The resulting object is pushed onto the stack, to be
        subsequently stored by a STORE_FAST instruction.

        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        mod = self.vm.top()
        if not hasattr(mod, name):
            # FIXME: figure out how to fake a traceback object
            # TODO: Create PyTraceBack_Here function.
            self.vm.last_exception = (ImportError, name,
                                      [self.vm.frame.f_code.co_filename, "bogus_function()", self.vm.frame.f_lineno])
            return "reexception"

        self.vm.push(getattr(mod, name))

    ## Jumps

    def JUMP_FORWARD(self, jump_offset):
        """Increments bytecode counter by jump.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """

        self.vm.jump(jump_offset)

    def JUMP_IF_TRUE(self, jump_offset):
        """
        If TOS is true, increment the bytecode counter by delta. TOS is
        left on the stack.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """
        val = self.vm.top()
        if val:
            self.vm.jump(jump_offset)

    def JUMP_IF_FALSE(self, jump_offset):
        """
        If TOS is false, increment the bytecode counter by delta. TOS is
        not changed.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """
        val = self.vm.top()
        if not val:
            self.vm.jump(jump_offset)

    def JUMP_ABSOLUTE(self, target):
        """Set bytecode counter to target."""
        self.vm.jump(target)

    # end Jump section

    def FOR_ITER(self, jump_offset):
        """
        TOS is an iterator. Call its next() method. If this yields a new
        value, push it on the stack (leaving the iterator below
        it). If the iterator indicates it is exhausted TOS is popped,
        and the bytecode counter is incremented by delta.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """

        iterobj = self.vm.top()
        try:
            v = next(iterobj)
            self.vm.push(v)
        except StopIteration:
            self.vm.pop()
            self.vm.jump(jump_offset)

    def LOAD_GLOBAL(self, name):
        """
        Loads the global named co_names[namei] onto the stack.

        Note: name = co_names[namei] set in parse_byte_and_args()
        """
        f = self.vm.frame
        if name in f.f_globals:
            val = f.f_globals[name]
        elif name in f.f_builtins:
            val = f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        self.vm.push(val)

    def SETUP_LOOP(self, jump_offset):
        """
        Pushes a block for a loop onto the block stack. The block spans
        from the current instruction with a size of delta bytes.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """
        self.vm.push_block("loop", jump_offset)

    def SETUP_EXCEPT(self, jump_offset):
        """
        Pushes a try block from a try-except clause onto the block
        stack. delta points to the first except block.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """

        self.vm.push_block("setup-except", jump_offset)

    def SETUP_FINALLY(self, jump_offset):
        """
        Pushes a try block from a try-except clause onto the block
        stack. delta points to the finally block.

        Note: jump = delta + f.f_lasti set in parse_byte_and_args()
        """
        self.vm.push_block("finally", jump_offset)

    def STORE_MAP(self):
        """
        Store a key and value pair in a dictionary. Pops the key and value while leaving the dictionary on the stack.
        """
        the_map, val, key = self.vm.popn(3)
        the_map[key] = val
        self.vm.push(the_map)

    ## some (but not all) Names

    def LOAD_FAST(self, name):
        """
        Pushes a reference to the local co_varnames[var_num] onto the stack.
        """
        if name in self.vm.frame.f_locals:
            val = self.vm.frame.f_locals[name]
        else:
            raise UnboundLocalError(
                "local variable '%s' referenced before assignment" % name
            )
        self.vm.push(val)

    def STORE_FAST(self, var_num):
        """Stores TOS into the local co_varnames[var_num]."""
        self.vm.frame.f_locals[var_num] = self.vm.pop()

    def DELETE_FAST(self, var_num):
        """Deletes local co_varnames[var_num]."""
        del self.vm.frame.f_locals[var_num]

    def LOAD_CLOSURE(self, i):
        """
        Pushes a reference to the cell contained in slot i of the cell and
        free variable storage. The name of the variable is co_cellvars[i] if i is less
        than the length of co_cellvars. Otherwise it is co_freevars[i -len(co_cellvars)].
        """
        self.vm.push(self.vm.frame.cells[i])

    def LOAD_DEREF(self, i):
        """
        Loads the cell contained in slot i of the cell and free variable
        storage. Pushes a reference to the object the cell contains on the
        stack.
        """
        self.vm.push(self.vm.frame.cells[i].get())

    def STORE_DEREF(self, name):
        """
        Stores TOS into the cell contained in slot i of the cell and free variable storage.
        """
        self.vm.frame.cells[name].set(self.vm.pop())

    # End names

    def IMPORT_STAR(self):
        """Loads all symbols not starting with '_' directly from the module
        TOS to the local namespace. The module is popped after loading all
        names. This opcode implements from module import *.
        """
        # TODO: this doesn't use __all__ properly.
        mod = self.vm.pop()
        for attr in dir(mod):
            if attr[0] != "_":
                self.vm.frame.f_locals[attr] = getattr(mod, attr)

    def EXEC_STMT(self):
        """
        Implements exec TOS2,TOS1,TOS. The compiler fills missing
        optional parameters with None.
        """
        stmt, globs, locs = self.vm.popn(3)
        six.exec_(stmt, globs, locs)

    def DUP_TOPX(self, count):
        """
        Duplicate count items, keeping them in the same order. Due to
        implementation limits, count should be between 1 and 5 inclusive.
        """
        items = self.vm.popn(count)
        for i in [1, 2]:
            self.vm.push(*items)

    # Not ready for prime time.
    # def END_FINALLY(self):
    #     """
    #     Terminates a "finally" clause. The interpreter recalls whether the
    #     exception has to be re-raised, or whether the function
    #     returns, and continues with the outer-next block.
    #     """
    #     v = self.vm.pop()
    #     if isinstance(v, str):
    #         why = v
    #         if why in ("return", "continue"):
    #             self.return_value = self.vm.pop()
    #         if why == "silenced":  # PYTHON3
    #             block = self.vm.pop_block()
    #             assert block.type == "except-handler"
    #             self.vm.unwind_block(block)
    #             why = None
    #     elif v is None:
    #         why = None
    #     elif issubclass(v, BaseException):
    #         exctype = v
    #         val = self.vm.pop()
    #         tb = self.vm.pop()
    #         self.last_exception = (exctype, val, tb)
    #         why = "reraise"
    #     else:  # pragma: no cover
    #         raise self.VirtualMachineError("Confused END_FINALLY")
    #     return why

    def BUILD_CLASS(self):
        """
        Creates a new class object. TOS is the methods dictionary, TOS1 the
        tuple of the names of the base classes, and TOS2 the class name.
        """
        name, bases, methods = self.vm.popn(3)
        self.vm.push(type(name, bases, methods))

    # This opcode changes in 3.3
    def WITH_CLEANUP(self):
        """Cleans up the stack when a "with" statement block exits. On top of
        the stack are 1–3 values indicating how/why the finally clause
        was entered:

        * TOP = None
        * (TOP, SECOND) = (WHY_{RETURN,CONTINUE}), retval
        * TOP = WHY_*; no retval below it
        * (TOP, SECOND, THIRD) = exc_info()

        Under them is EXIT, the context manager’s __exit__() bound method.

        In the last case, EXIT(TOP, SECOND, THIRD) is called,
        otherwise EXIT(None, None, None).

        EXIT is removed from the stack, leaving the values above it in
        the same order. In addition, if the stack represents an
        exception, and the function call returns a ‘true’ value, this
        information is “zapped”, to prevent END_FINALLY from
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
            raise self.VirtualMachineError("Confused WITH_CLEANUP")
        exit_ret = exit_func(u, v, w)
        err = (u is not None) and bool(exit_ret)
        if err:
            # An error occurred, and was suppressed
            self.vm.popn(3)
            self.vm.push(None)

    def MAKE_FUNCTION(self, argc):
        """
        Pushes a new function object on the stack. TOS is the code
        associated with the function. The function object is defined to have
        argc default parameters, which are found below TOS.
        """
        name = None
        code = self.vm.pop()
        defaults = self.vm.popn(argc)
        globs = self.vm.frame.f_globals
        fn = Function(name, code, globs, defaults, None, self.vm)
        fn.version = self.version
        self.vm.push(fn)

    def MAKE_CLOSURE(self, argc):
        """
        Creates a new function object, sets its func_closure slot, and
        pushes it on the stack. TOS is the code associated with the
        function. If the code object has N free variables, the next N
        items on the stack are the cells for these variables. The
        function also has argc default parameters, where are found
        before the cells.
        """
        if self.version >= 3.3:
            name = self.vm.pop()
        else:
            name = None
        closure, code = self.vm.popn(2)
        defaults = self.vm.popn(argc)
        globs = self.vm.frame.f_globals
        fn = Function(name, code, globs, defaults, closure, self.vm)
        self.vm.push(fn)

    def CALL_FUNCTION(self, arg):
        """
        Calls a callable object.
        The low byte of argc indicates the number of positional
        arguments, the high byte the number of keyword arguments.

        The stack contains keyword arguments on top (if any), then the
        positional arguments below that (if any), then the callable
        object to call below that.

        Each keyword argument is represented with two values on the
        stack: the argument’s name, and its value, with the argument's
        value above the name on the stack. The positional arguments
        are pushed in the order that they are passed in to the
        callable object, with the right-most positional argument on
        top. CALL_FUNCTION pops all arguments and the callable object
        off the stack, calls the callable object with those arguments,
        and pushes the return value returned by the callable object.
        """
        return self.vm.call_function(arg, [], {})

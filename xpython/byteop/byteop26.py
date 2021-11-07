# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6

Note: this is subclassed so later versions may use operations from here.
"""

import sys

from xdis.version_info import PYTHON_VERSION_TRIPLE

try:
    import importlib
except ImportError:
    importlib = None

from xpython.byteop.byteop import fmt_binary_op
from xpython.byteop.byteop24 import fmt_make_function, Version_info
from xpython.byteop.byteop25 import ByteOp25
from xpython.pyobj import Function


class ByteOp26(ByteOp25):
    def __init__(self, vm):
        super(ByteOp26, self).__init__(vm)
        self.stack_fmt["IMPORT_NAME"] = fmt_binary_op
        self.stack_fmt["MAKE_CLOSURE"] = fmt_make_function

        # Fake up version information
        self.hexversion = 0x20609F0
        self.version = "2.6.9 (default, Oct 27 1955, 00:00:00)\n[x-python]"
        self.version_info = Version_info(2, 6, 9, "final", 0)

    # Right now 2.6 is largely the same as 2.5 here. How nice!

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

        if importlib is not None:
            module_spec = importlib.util.find_spec(name)
            module = importlib.util.module_from_spec(module_spec)

            load_module = (
                module_spec.loader.exec_module
                if hasattr(module_spec.loader, "exec_module")
                else module_spec.loader.load_module
            )
            load_module(module)

        elif PYTHON_VERSION_TRIPLE >= (3, 0):
            # This should make a *copy* of the module so we keep interpreter and
            # intpreted programs separate.
            # See below for how we handle "sys" import
            if level < 0:
                level = 0
            module = importlib.__import__(
                name, frame.f_globals, frame.f_locals, fromlist, level
            )
        else:
            module = __import__(name, frame.f_globals, frame.f_locals, fromlist, level)

        # FIXME: generalize this
        if name in sys.builtin_module_names:
            # FIXME: do more here.
            if PYTHON_VERSION_TRIPLE[:2] != self.version_info[:2]:
                if name == "sys":
                    module.version_info = self.version_info
                    module.version = self.version
                    pass
                pass
        self.vm.push(module)

    def MAKE_CLOSURE(self, argc):
        """
        Creates a new function object, sets its func_closure slot, and
        pushes it on the stack. TOS is the code associated with the
        function. If the code object has N free variables, the next N
        items on the stack are the cells for these variables. The
        function also has argc default parameters, where are found
        before the cells.
        """
        if self.version_info[:2] >= (3, 3):
            name = self.vm.pop()
        else:
            name = None
        closure, code = self.vm.popn(2)
        defaults = self.vm.popn(argc)
        globs = self.vm.frame.f_globals
        fn = Function(name, code, globs, defaults, closure, self.vm)
        self.vm.push(fn)

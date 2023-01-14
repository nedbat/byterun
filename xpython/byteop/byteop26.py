# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations for Python 2.6

Note: this is subclassed so later versions may use operations from here.
"""

import os
import sys

from xdis.version_info import PYTHON_VERSION_TRIPLE

import xpython.stdlib

try:
    import importlib
except ImportError:
    importlib = None

from xpython.byteop.byteop import fmt_binary_op
from xpython.byteop.byteop24 import Version_info, fmt_make_function
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

        # Should we replace import "name" with a compatabliity version?
        if name in xpython.stdlib.__all__:
            name = f"xpython.stdlib.{name}"

        # if importlib is not None:
        #     module_spec = importlib.util.find_spec(name)
        #     module = importlib.util.module_from_spec(module_spec)

        #     load_module = (
        #         module_spec.loader.exec_module
        #         if hasattr(module_spec.loader, "exec_module")
        #         else module_spec.loader.load_module
        #     )
        #     load_module(module)

        # elif PYTHON_VERSION_TRIPLE >= (3, 0):
        #     # This should make a *copy* of the module so we keep interpreter and
        #     # interpreted programs separate.
        #     # See below for how we handle "sys" import
        #     # FIXME: should split on ".". Doesn't work for, say, os.path
        #     if level < 0:
        #         level = 0
        #     module = importlib.__import__(
        #         name, frame.f_globals, frame.f_locals, fromlist, level
        #     )
        # else:
        #     module = __import__(name, frame.f_globals, frame.f_locals, fromlist, level)

        # INVESTIGATE: the above doesn't work for things like "import os.path as osp"
        # The module it finds ins os.posixpath which doesn't have a "path" attribute
        # while the below finds "os" which does have a "path" attribute.
        #
        assert level >= -1, f"Invalid Level number {level} on IMPORT_NAME"
        module = None
        if level == -1:
            # In Python 2.6 added the level parameter and it was -1 by default until but not including 3.0.
            # -1 means try relative imports before absolute imports.
            if PYTHON_VERSION_TRIPLE >= (3, 0):
                # FIXME: give warning that we can't handle absolute import. Or fix up code to handle possible absolute import.
                level = 0
            else:
                module = __import__(
                    "." + os.sep + name,
                    frame.f_globals,
                    frame.f_locals,
                    fromlist,
                    level,
                )

        if module is None:
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

    def MAKE_CLOSURE(self, argc: int):
        """
        Creates a new function object, sets its ``func_closure`` slot, and
        pushes it on the stack. TOS is the code associated with the
        function, TOS1 the tuple containing cells for the closure’s
        free variables. The function also has ``argc`` default parameters,
        which are found below the cells.
        """
        name = None
        closure, code = self.vm.popn(2)
        defaults = self.vm.popn(argc)
        globs = self.vm.frame.f_globals
        fn = Function(name, code, globs, defaults, closure, self.vm)
        self.vm.push(fn)

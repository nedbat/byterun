# -*- coding: utf-8 -*-
"""Bytecode Interpreter operations base class

Note: this is subclassed. Later versions use operations from here.
"""
from __future__ import print_function, division

import inspect
import logging
import sys
from xdis import PYTHON_VERSION
from xpython.pyobj import Function
from xpython.buildclass import build_class

log = logging.getLogger(__name__)

class ByteOpBase(object):
    def __init__(self, vm):
        self.vm = vm
        # Convenience variables
        self.version = vm.version
        self.is_pypy = vm.is_pypy

        # Set this lazily in "convert_method_native_func
        self.method_func_access = None

    def build_container(self, count, container_fn):
        elts = self.vm.popn(count)
        self.vm.push(container_fn(elts))

    def call_function_with_args_resolved(self, func, posargs, namedargs):
        frame = self.vm.frame
        if hasattr(func, "im_func"):
            # Methods get self as an implicit first parameter.
            if func.im_self is not None:
                posargs.insert(0, func.im_self)
            # The first parameter must be the correct type.
            if not isinstance(posargs[0], func.im_class):
                raise TypeError(
                    "unbound method %s() must be called with %s instance "
                    "as first argument (got %s instance instead)"
                    % (
                        func.im_func.func_name,
                        func.im_class.__name__,
                        type(posargs[0]).__name__,
                    )
                )
            func = func.im_func

        # FIXME: should we special casing in a function?
        if inspect.isbuiltin(func):
            log.debug("handling built-in function %s" % func.__name__)
            if func == globals:
                # Use the frame's globals(), not the interpreter's
                self.vm.push(frame.f_globals)
                return
            elif func == locals:
                # Use the frame's locals(), not the interpreter's
                self.vm.push(frame.f_globals)
                return
            elif (self.is_pypy or self.version != PYTHON_VERSION) and PYTHON_VERSION >= 3.4:
                if func == __build_class__:
                    # later __build_class__() works only bytecode that matches the CPython interpeter,
                    # so use Darius' version instead.

                    # Try to convert to an interpreter function which is needed by build_class
                    if True: # self.version == PYTHON_VERSION and self.is_pypy != IS_PYPY:
                        assert len(posargs) > 0
                        posargs[0] = self.convert_native_to_Function(frame, posargs[0])

                    retval = build_class(self.vm.opc, *posargs, **namedargs)
                    self.vm.push(retval)
                    return

        if inspect.isfunction(func):
            # Try to convert to an interpreter function so we can interpret it.
            if func in self.vm.fn2native:
                func = self.vm.fn2native[func]
            elif False: # self.vm.version < 3.0:
                # Not quite ready. See 3.7 test_asyncgen.py for an
                # example of code that comes here. In that test, the
                # LOAD_GLOBAL '_ignore_deprecated_imports' fails to
                # find the global. '_ignore_deprecated_imports' is a method name
                # in test.support module of test/support/__init__.py.
                # In Python 2.X we work around a similar problem by
                # not tying to handle functions with closures.
                assert len(posargs) > 0
                posargs[0] = self.convert_native_to_Function(frame, posargs[0])

        if inspect.isfunction(func):
            log.debug("calling native function %s" % func.__name__)

        retval = func(*posargs, **namedargs)
        self.vm.push(retval)

    def call_function(self, argc, args, kwargs):
        namedargs = {}
        lenKw, lenPos = divmod(argc, 256)
        for i in range(lenKw):
            key, val = self.vm.popn(2)
            namedargs[key] = val
        namedargs.update(kwargs)
        posargs = self.vm.popn(lenPos)
        posargs.extend(args)

        func = self.vm.pop()
        self.call_function_with_args_resolved(func, posargs, namedargs)

    def convert_native_to_Function(self, frame, func):
        assert inspect.isfunction(func) or isinstance(func, Function)
        slots = {
            "kwdefaults" : {},
            "annotations": {},
        }
        if self.vm.version >= 3.0:
            slots["globs"] = frame.f_globals
            arg2attr = {
                "code": "__code__",
                "name": "__name__",
                "argdefs": "__defaults__",
                "kwdefaults": "__kwdefaults__",
                "annotations": "__annotations__",
                "closure": "__closure__",
                # FIXME: add __qualname__, __doc__
                # and __module__
            }
        else:
            slots["kwdefaults"] = {}
            slots["annotations"] = {}
            arg2attr = {
                "code": "func_code",
                "name": "__name__",
                "argdefs": "func_defaults",
                "globs": "func_globals",
                "annotations": "doesn't exist",
                "closure": "func_closure",
                # FIXME: add __doc__
                # and __module__
            }

        for argname, attribute in arg2attr.items():
            if hasattr(func, attribute):
                slots[argname] = getattr(func, attribute)

        closure = getattr(func, arg2attr["closure"])
        if not closure:
            # FIXME: we don't know how to convert functions with closures yet.
            native_func = func

            func = Function(
                slots["name"],
                slots["code"],
                slots["globs"],
                slots["argdefs"],
                slots["closure"],
                self.vm,
                slots["kwdefaults"],
                slots["annotations"],
            )
            self.vm.fn2native[native_func] = func
        return func

    def lookup_name(self, name):
        """Returns the value in the current frame associated for name"""
        frame = self.vm.frame
        if name in frame.f_locals:
            val = frame.f_locals[name]
        elif name in frame.f_globals:
            val = frame.f_globals[name]
        elif name in frame.f_builtins:
            val = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        return val

    def print_item(self, item, to=None):
        if to is None:
            to = sys.stdout

        # Python 2ish has file.softspace whereas
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

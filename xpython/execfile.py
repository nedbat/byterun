"""Execute files of Python code."""

import os
import sys
import tokenize
import mimetypes
from xdis import load_module, PYTHON_VERSION, IS_PYPY

from xpython.vm import format_instruction, PyVM, PyVMUncaughtException
from xpython.vmtrace import PyVMTraced
from xpython.version import SUPPORTED_PYTHON, SUPPORTED_BYTECODE, SUPPORTED_PYPY

# To silence the "import imp" DeprecationWarning below
import warnings

warnings.filterwarnings("ignore")
import imp

# This code is ripped off from coverage.py.  Define things it expects.
try:
    open_source = tokenize.open  # pylint: disable=E1101
except:

    def open_source(fname):
        """Open a source file the best way."""
        return open(fname, "rU")


class CannotCompileError(Exception):
    """For raising errors when we have a Compile eror."""

    pass


class WrongBytecodeError(Exception):
    """For raising errors when we have the wrong bytecode."""

    pass


class NoSourceError(Exception):
    """For raising errors when we can't find source code."""

    pass


def exec_code_object(
    code,
    env,
    python_version=PYTHON_VERSION,
    is_pypy=IS_PYPY,
    callback=None,
    format_instruction=format_instruction,
):
    if callback:
        vm = PyVMTraced(callback, python_version, is_pypy,
                        format_instruction_func=format_instruction)
        try:
            vm.run_code(code, f_globals=env)
        except PyVMUncaughtException:
            vm.last_exception = event_arg = (
                vm.last_exception[0],
                vm.last_exception[1],
                vm.last_traceback,
            )
            callback("fatal", 0, "fatalOpcode", 0, -1, event_arg, [], vm)
    else:
        vm = PyVM(python_version, is_pypy, format_instruction_func=format_instruction)
        try:
            vm.run_code(code, f_globals=env)
        except PyVMUncaughtException:
            pass


def get_supported_versions(is_pypy, is_bytecode):
    if is_bytecode:
        supported_versions = SUPPORTED_PYPY if IS_PYPY else SUPPORTED_BYTECODE
        mess = (
            "PYPY 2.7, 3.2, 3.5 and 3.6"
            if is_pypy
            else "CPython 2.4 .. 2.7, 3.2 .. 3.7"
        )
    else:
        supported_versions = SUPPORTED_PYPY if IS_PYPY else SUPPORTED_PYTHON
        mess = "PYPY 2.7, 3.2, 3.5 and 3.6" if is_pypy else "CPython 2.7, 3.2 .. 3.7"
    return supported_versions, mess


# from coverage.py:

try:
    # In Py 2.x, the builtins were in __builtin__
    BUILTINS = sys.modules["__builtin__"]
except KeyError:
    # In Py 3.x, they're in builtins
    BUILTINS = sys.modules["builtins"]


def rsplit1(s, sep):
    """The same as s.rsplit(sep, 1), but works in 2.3"""
    parts = s.split(sep)
    return sep.join(parts[:-1]), parts[-1]


def run_python_module(modulename, args):
    """Run a python module, as though with ``python -m name args...``.

    `modulename` is the name of the module, possibly a dot-separated name.
    `args` is the argument array to present as sys.argv, including the first
    element naming the module being executed.

    """
    openfile = None
    glo, loc = globals(), locals()
    try:
        try:
            # Search for the module - inside its parent package, if any - using
            # standard import mechanics.
            if "." in modulename:
                packagename, name = rsplit1(modulename, ".")
                package = __import__(packagename, glo, loc, ["__path__"])
                searchpath = package.__path__
            else:
                packagename, name = None, modulename
                searchpath = None  # "top-level search" in imp.find_module()
            openfile, pathname, _ = imp.find_module(name, searchpath)

            # Complain if this is a magic non-file module.
            if openfile is None and pathname is None:
                raise NoSourceError("module does not live in a file: %r" % modulename)

            # If `modulename` is actually a package, not a mere module, then we
            # pretend to be Python 2.7 and try running its __main__.py script.
            if openfile is None:
                packagename = modulename
                name = "__main__"
                package = __import__(packagename, glo, loc, ["__path__"])
                searchpath = package.__path__
                openfile, pathname, _ = imp.find_module(name, searchpath)
        except ImportError:
            _, err, _ = sys.exc_info()
            raise NoSourceError(str(err))
    finally:
        if openfile:
            openfile.close()

    # Finally, hand the file off to run_python_file for execution.
    args[0] = pathname
    run_python_file(pathname, args, package=packagename)


def run_python_file(
        filename, args, package=None, callback=None, format_instruction=format_instruction
):
    """Run a python file as if it were the main program on the command line.

    `filename` is the path to the file to execute, it need not be a .py file.
    `args` is the argument array to present as sys.argv, including the first
    element naming the file being executed.  `package` is the name of the
    enclosing package, if any.

    If `callback` is not None, it is a function which is called back as the
    execution progresses. This can be used for example in a debugger, or
    for custom tracing or statistics gathering.
    """
    # Create a module to serve as __main__
    old_main_mod = sys.modules["__main__"]
    main_mod = imp.new_module("__main__")
    sys.modules["__main__"] = main_mod
    main_mod.__file__ = filename
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS

    # set sys.argv and the first path element properly.
    old_argv = sys.argv
    old_path0 = sys.path[0]

    # note: the type of args is na tuple; we want type(sys.argv) == list
    sys.argv = [filename] + list(args)

    if package:
        sys.path[0] = ""
    else:
        sys.path[0] = os.path.abspath(os.path.dirname(filename))

    is_pypy = IS_PYPY
    try:
        # Open the source or bytecode file.
        try:
            mime = mimetypes.guess_type(filename)
            if mime == ("application/x-python-code", None):
                (
                    python_version,
                    timestamp,
                    magic_int,
                    code,
                    is_pypy,
                    source_size,
                    sip_hash,
                ) = load_module(filename)
                supported_versions, mess = get_supported_versions(
                    is_pypy, is_bytecode=True
                )
                if python_version not in supported_versions:
                    raise WrongBytecodeError(
                        "We only support byte code for %s: %r is %2.1f bytecode"
                        % (mess, filename, python_version)
                    )
                pass
            else:
                source_file = open_source(filename)
                try:
                    source = source_file.read()
                finally:
                    source_file.close()

                supported_versions, mess = get_supported_versions(
                    IS_PYPY, is_bytecode=False
                )
                if PYTHON_VERSION not in supported_versions:
                    raise CannotCompileError(
                        "We need %s to compile source code; you are running Python %s"
                        % (mess, PYTHON_VERSION)
                    )

                # We have the source.  `compile` still needs the last line to be clean,
                # so make sure it is, then compile a code object from it.
                if not source or source[-1] != "\n":
                    source += "\n"
                code = compile(source, filename, "exec")
                python_version = PYTHON_VERSION

        except (IOError, ImportError):
            raise NoSourceError("No file to run: %r" % filename)

        # Execute the source file.
        exec_code_object(
            code,
            main_mod.__dict__,
            python_version,
            is_pypy,
            callback,
            format_instruction=format_instruction,
        )

    finally:
        # Restore the old __main__
        sys.modules["__main__"] = old_main_mod

        # Restore the old argv and path
        sys.argv = old_argv
        sys.path[0] = old_path0


def run_python_string(
    source, args, package=None, callback=None, format_instruction=format_instruction
):
    """Run a python string as if it were the main program on the command line.
    """
    # Create a module to serve as __main__
    old_main_mod = sys.modules["__main__"]
    main_mod = imp.new_module("__main__")
    sys.modules["__main__"] = main_mod
    fake_path = main_mod.__file__ = "<string %s>" % source[:20]
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS

    # Set sys.argv and the first path element properly.
    old_path0 = sys.path[0]
    sys.argv = [fake_path] + list(args)

    try:
        supported_versions, mess = get_supported_versions(IS_PYPY, is_bytecode=False)
        if PYTHON_VERSION not in supported_versions:
            raise CannotCompileError(
                "We need %s to compile source code; you are running %s"
                % (mess, PYTHON_VERSION)
            )

        # `compile` still needs the last line to be clean,
        # so make sure it is, then compile a code object from it.
        if not source or source[-1] != "\n":
            source += "\n"
        code = compile(source, fake_path, "exec")
        python_version = PYTHON_VERSION

        # Execute the source string.
        exec_code_object(code, main_mod.__dict__, python_version, IS_PYPY, callback,
                         format_instruction=format_instruction,
        )

    finally:
        # Restore the old __main__
        sys.modules["__main__"] = old_main_mod

        # Restore the old argv and path
        sys.path[0] = old_path0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: execfile.py <filename> args")
        sys.exit(1)
    run_python_file(sys.argv[1], sys.argv[2:])

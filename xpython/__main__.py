"""A main program for xpython."""

import click
import logging
import sys

from xpython import execfile
from xpython.vm import PyVMRuntimeError
from xpython.version import VERSION
from xdis import PYTHON_VERSION, IS_PYPY

def version_message():
    platform = "PyPy " if IS_PYPY else "C"
    mess = "%s running from %sPython %s" % (
        VERSION, platform, PYTHON_VERSION
    )
    return mess

@click.command()
@click.version_option(version_message(), "-V", "--version")
@click.option("-m", "--module", default=False,
              help="PATH is a module name, not a Python main program")
@click.option("-v", "--verbose", count=True,
              help="verbosity level in tracing.\n"
              "Can be supplied multiple times to increase verbosity.")
@click.option("-c", "--command-to-run",
              help="program passed in as a string", required=False)
@click.argument("path", nargs=1, type=click.Path(readable=True), required=False)
@click.argument("args", nargs=-1)
def main(module, verbose, command_to_run, path, args):
    """
    Runs Python programs or bytecode using a bytecode interpreter written in Python.
    """
    if module:
        run_fn = execfile.run_python_module
    else:
        run_fn = execfile.run_python_file

    if verbose > 1:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    if command_to_run:
        if path or args:
            print("You must pass either a file name or a command string, not both.")
            sys.exit(4)
        path = command_to_run
        run_fn = execfile.run_python_string
    elif not path:
        print("You must pass either a file name or a command string, neither found.")
        sys.exit(4)

    try:
        run_fn(path, args)
    except PyVMRuntimeError:
        # Tracebacks and error messages should been previously printed
        sys.exit(10)
    except execfile.CannotCompileError as e:
        print(e)
        sys.exit(1)
        pass
    except execfile.NoSourceError as e:
        if verbose > 1:
            raise
        print(e)
        sys.exit(2)
        pass
    except execfile.WrongBytecodeError as e:
        if verbose > 1:
            raise
        print(e)
        sys.exit(3)
        pass
    except SystemExit:
        # Program ran sys.exit();
        # Respect that.
        raise

if __name__ == "__main__":
    main(auto_envvar_prefix="XPYTHON")

"""A main program for xpython."""

import click
import logging
import sys

from xpython import execfile
from xpython.version import VERSION

@click.command()
@click.version_option(version=VERSION)
@click.option("-m", "--module", default=False,
              help="PATH is a module name, not a Python main program")
@click.option("-d", "--debug-level", default=0,
              help="debug output level in running")
@click.argument("path", nargs=1, type=click.Path(readable=True), required=True)
@click.argument("args", nargs=-1)
def main(module, debug_level, path, args):
    """
    Runs Python programs or bytecode using a bytecode interpreter written in Python.
    """
    if module:
        run_fn = execfile.run_python_module
    else:
        run_fn = execfile.run_python_file

    if debug_level > 1:
        level = logging.DEBUG
    elif debug_level == 1:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    try:
        run_fn(path, args)
    except execfile.CannotCompile as e:
        if debug_level > 1:
            raise
        print(e)
        sys.exit(1)
        pass
    except execfile.NoSource as e:
        if debug_level > 1:
            raise
        print(e)
        sys.exit(2)
        pass
    except execfile.WrongBytecode as e:
        if debug_level > 1:
            raise
        print(e)
        sys.exit(3)
        pass

if __name__ == "__main__":
    main(auto_envvar_prefix="XPYTHON")

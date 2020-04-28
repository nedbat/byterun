"""A main program for xpython."""

from xdis import PYTHON_VERSION
import argparse
import logging

from xpython import execfile

def main():
    if PYTHON_VERSION not in (3.3, 2.7):
        print("Warning: this program is only known to run under Python 2.7 or 3.3, you have: %s" % PYTHON_VERSION)

    parser = argparse.ArgumentParser(
        prog="xpython",
        description="Run Python programs with a Python bytecode interpreter.",
    )
    parser.add_argument(
        '-m', dest='module', action='store_true',
        help="prog is a module name, not a file name.",
    )
    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        help="trace the execution of the bytecode.",
    )
    parser.add_argument(
        'prog',
        help="The program to run.",
    )
    parser.add_argument(
        'args', nargs=argparse.REMAINDER,
        help="Arguments to pass to the program.",
    )
    args = parser.parse_args()

    if args.module:
        run_fn = execfile.run_python_module
    else:
        run_fn = execfile.run_python_file

    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=level)

    argv = [args.prog] + args.args
    run_fn(args.prog, argv)

if __name__ == "__main__":
    main()

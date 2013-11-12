"""A main program for Byterun."""

import argparse
import logging

from . import execfile

parser = argparse.ArgumentParser()
parser.add_argument('-m', dest='module', action='store_true')
parser.add_argument('to_run')
parser.add_argument('arg', nargs=argparse.REMAINDER)
args = parser.parse_args()

if args.module:
    run_fn = execfile.run_python_module
else:
    run_fn = execfile.run_python_file

logging.basicConfig(
    level=logging.INFO,
)

argv = [args.to_run] + args.arg
run_fn(args.to_run, argv)

#!/usr/bin/env python
import sys
import os.path as osp

def get_srcdir():
    filename = osp.normcase(osp.dirname(__file__))
    return osp.realpath(filename)

if len(sys.argv) != 2:
    print("Usage: compile-file.py *byte-compiled-file*")
    sys.exit(1)
source = sys.argv[1]

assert source.endswith('.py')
basename = source[:-3]

# We do this crazy conversion from float to support Python 2.6 which
# doesn't support version_major, and has a bug in
# floating point so we can't divide 26 by 10 and get
# 2.6
PY_VERSION = sys.version_info[0] + (sys.version_info[1] / 10.0)

bytecode_path = osp.join(get_srcdir(), "..", "bytecode-%s" % PY_VERSION, "%s.pyc" % basename)

import py_compile
print("compiling %s to %s" % (source, bytecode_path))
py_compile.compile(source, bytecode_path, source)
import os
os.system("xpython %s" % bytecode_path)

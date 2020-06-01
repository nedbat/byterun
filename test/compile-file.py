#!/usr/bin/env python
import sys
import os.path as osp
from xdis import IS_PYPY

# We do this crazy conversion from float to support Python 2.6 which
# doesn't support version_major, and has a bug in
# floating point so we can't divide 26 by 10 and get
# 2.6
PY_VERSION = sys.version_info[0] + (sys.version_info[1] / 10.0)

def get_srcdir():
    if PY_VERSION > 2.5:
        return osp.relpath(osp.normcase(osp.dirname(__file__)))
    else:
        return osp.normcase(osp.dirname(__file__))

if len(sys.argv) != 2:
    print("Usage: compile-file.py *byte-compiled-file*")
    sys.exit(1)

if PY_VERSION > 2.6:
    source = osp.normpath(osp.relpath(sys.argv[1]))
else:
    source = osp.normpath(sys.argv[1])

assert source.endswith('.py')
basename = osp.basename(source[:-3])

if IS_PYPY:
    platform="pypy"
else:
    platform=""

bytecode_path = osp.normpath(osp.join(get_srcdir(),
                                      "bytecode-%s%s" % (platform, PY_VERSION),
                                      "%s.pyc" % basename))

import py_compile
print("compiling %s to %s" % (source, bytecode_path))
py_compile.compile(source, bytecode_path, source)
if PY_VERSION >= 2.7:
    import os
    os.system("xpython %s" % bytecode_path)

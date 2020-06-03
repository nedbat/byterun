"""Testing intepreting a different bytcode from the one the Python interpreter is using."""
from __future__ import print_function

try:
    import vmtest
except ImportError:
    from . import vmtest

from glob import iglob
import os
from xdis import PYTHON_VERSION

# In the dictionary below,a
# The key is a Python version and
# the value is a list of Python bytecode
# different from itself that it should be able to handle
COMPATABILITY_MATRIX = {
    2.7: (2.6, 2.5, 2.4),
    3.2: (),

    # TODO: work on these. The list is not too large
    3.3: (3.2,),
    3.4:  (3.3,),

    3.5: (3.7, 3.6, 3.4),
    3.6: (3.5, 3.4, 3.3),
    3.7: (3.6, 3.4),
}

# In addition, PyPy and CPython *should* be inter compatible,
# since we should take pains to handle PyPy's LOOKUP_METHOD and
# CALL_METHOD.

# How to increase compatablity above.
# 1. Write a replacement for builtin build_class
# 2. The `inspect` module is used to grock function calls.
#    it has checks for iscode and so on. Change those to
#    be use duck typing.

STARS = "*" * 10
class TestCompat(vmtest.VmTestCase):

    if not os.environ.get("SKIP_COMPAT", False):
        def test_cross_version_compatablity(self):
            compatible_versions = COMPATABILITY_MATRIX.get(PYTHON_VERSION, ())
            import logging
            logging.basicConfig(level=logging.WARN)
            for version in compatible_versions:
                print("%s%s%s" % (STARS, version, STARS))
                os.chdir(os.path.join(vmtest.srcdir, "bytecode-%s" % version))
                for bytecode_file in iglob("*.pyc"):
                    # print(bytecode_file, version)
                    self.assert_runs_ok(bytecode_file, arg_type="bytecode-file")

if __name__ == "__main__":
    import unittest
    unittest.main()

    # t = TestCompat("test_cross_version_compatablity")
    # t.test_cross_version_compatablity()

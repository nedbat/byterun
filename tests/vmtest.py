"""Testing tools for xpython."""

from __future__ import print_function

from collections import deque
from xdis import load_module
from xdis.main import disco_loop, get_opcode
import os.path as osp
import inspect
import sys
import textwrap
import unittest

import six

from xpython.pyvm2 import VirtualMachine, VirtualMachineError

from xdis import PYTHON3, PYTHON_VERSION

# Make this false if you need to run the debugger inside a test.
CAPTURE_STDOUT = ('-s' not in sys.argv)
# Make this false to see the traceback from a failure inside pyvm2.
CAPTURE_EXCEPTION = 1


def get_srcdir():
    filename = osp.normcase(osp.dirname(__file__))
    return osp.realpath(filename)

examples_dir = osp.join(get_srcdir(), "examples")

def parent_function_name():
    if PYTHON_VERSION < 3.5:
        return inspect.stack()[2][3]
    else:
        return inspect.stack()[2].function

def dis_code(code, version, out):
    """Disassemble `code` and all the code it refers to."""
    opc = get_opcode(version, False)
    disco_loop(opc, version, deque([code]), out)


LINE_STR = "-" * 35

class VmTestCase(unittest.TestCase):

    def do_one(self):
        path = osp.join(examples_dir, parent_function_name())
        if PYTHON3:
            path += "-3.3.pyc"
            self.version = 3.3
        else:
            path += "-2.7.pyc"
            self.version = 2.7
        self.assert_ok(path, arg_type="bytecode-file")

    def assert_ok(self, path_or_code, raises=None, arg_type="string"):
        """Run `code` in our VM and in real Python: they behave the same."""

        if arg_type == "bytecode-file":
            self.version, timestamp, magic_int, code, pypy, source_size, sip_hash = load_module(path_or_code)
        else:
            self.version = PYTHON_VERSION
            if arg_type == "source":
                code_str = open(path_or_code, "r").read()
            else:
                assert arg_type == "string", "arg_type parameter needs to be either: bytecode-file, source or string; got %s" % arg_type
                code_str = textwrap.dedent(path_or_code)

            code = compile(code_str, "<%s>" % self.id(), "exec", 0, 1)

        real_stdout = sys.stdout

        # Print the disassembly so we'll see it if the test fails.
        dis_code(code, self.version, real_stdout)

        # Run the code through our VM.

        vm_stdout = six.StringIO()
        if CAPTURE_STDOUT:              # pragma: no branch
            sys.stdout = vm_stdout
        vm = VirtualMachine()

        vm_value = vm_exc = None
        try:
            vm_value = vm.run_code(code)
        except VirtualMachineError:         # pragma: no cover
            # If the VM code raises an error, show it.
            raise
        except AssertionError:              # pragma: no cover
            # If test code fails an assert, show it.
            raise
        except Exception as e:
            # Otherwise, keep the exception for comparison later.
            if not CAPTURE_EXCEPTION:       # pragma: no cover
                raise
            vm_exc = e
        finally:
            real_stdout.write("\n%s stdout %s\n\n" % (LINE_STR, LINE_STR))
            real_stdout.write(vm_stdout.getvalue())

        # Run the code through the real Python interpreter, for comparison.

        if self.version != PYTHON_VERSION:
            return

        py_stdout = six.StringIO()
        sys.stdout = py_stdout

        py_value = py_exc = None
        globs = {}
        try:
            py_value = eval(code, globs, globs)
        except AssertionError:              # pragma: no cover
            raise
        except Exception as e:
            py_exc = e

        sys.stdout = real_stdout

        self.assert_same_exception(vm_exc, py_exc)
        self.assertEqual(vm_stdout.getvalue(), py_stdout.getvalue())
        self.assertEqual(vm_value, py_value)
        if raises:
            self.assertIsInstance(vm_exc, raises)
        else:
            self.assertIsNone(vm_exc)

    def assert_same_exception(self, e1, e2):
        """Exceptions don't implement __eq__, check it ourselves."""
        self.assertEqual(str(e1), str(e2))
        self.assertIs(type(e1), type(e2))

if __name__ == "__main__":

    class TestOne(VmTestCase):
        def test_constant(self):
            self.do_one()

    t = TestOne("test_constant")
    t.test_constant()

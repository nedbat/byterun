"""Testing tools for byterun."""

from __future__ import print_function

import dis
import sys
import textwrap
import types
import unittest


from byterun.abstractvm import AbstractVirtualMachine
from byterun.pyvm2 import VirtualMachine, VirtualMachineError
import six

# Make this false if you need to run the debugger inside a test.
CAPTURE_STDOUT = ("-s" not in sys.argv)
# Make this false to see the traceback from a failure inside pyvm2.
CAPTURE_EXCEPTION = True


def dis_code(code):
    """Disassemble `code` and all the code it refers to."""
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            dis_code(const)

    print("")
    print(code)
    dis.dis(code)
    sys.stdout.flush()


def run_with_byterun(code, vmclass=VirtualMachine):
    real_stdout = sys.stdout
    try:
        # Run the code through our VM.
        vm_stdout = six.StringIO()
        if CAPTURE_STDOUT:              # pragma: no branch
            sys.stdout = vm_stdout
        vm = vmclass()

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
            real_stdout.write("-- stdout ----------\n")
            real_stdout.write(vm_stdout.getvalue())
        return vm_value, vm_stdout.getvalue(), vm_exc
    finally:
        sys.stdout = real_stdout


def run_with_eval(code):
    real_stdout = sys.stdout
    try:
        # Run the code through the real Python interpreter, for comparison.
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
        return py_value, py_stdout.getvalue(), py_exc
    finally:
        sys.stdout = real_stdout


class VmTestCase(unittest.TestCase):

    def assert_ok(self, code, raises=None):
        """Run `code` in our VM and in real Python: they behave the same."""

        code = textwrap.dedent(code)
        code = compile(code, "<%s>" % self.id(), "exec", 0, 1)

        # Print the disassembly so we'll see it if the test fails.
        dis_code(code)

        vm_value, vm_stdout_value, vm_exc = run_with_byterun(code)
        abstractvm_value, abstractvm_stdout_value, abstractvm_exc = (
            run_with_byterun(code, AbstractVirtualMachine))
        py_value, py_stdout_value, py_exc = run_with_eval(code)

        self.assert_same_exception(vm_exc, py_exc)
        self.assert_same_exception(abstractvm_exc, py_exc)
        self.assertEqual(vm_stdout_value, py_stdout_value)
        self.assertEqual(abstractvm_stdout_value, py_stdout_value)
        self.assertEqual(vm_value, py_value)
        self.assertEqual(abstractvm_value, py_value)
        if raises:
            self.assertIsInstance(vm_exc, raises)
            self.assertIsInstance(abstractvm_exc, raises)
        else:
            self.assertIsNone(vm_exc)
            self.assertIsNone(abstractvm_exc)

    def assert_same_exception(self, e1, e2):
        """Exceptions don't implement __eq__, check it ourselves."""
        self.assertEqual(str(e1), str(e2))
        self.assertIs(type(e1), type(e2))

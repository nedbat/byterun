"""Testing tools for byterun."""

import dis
import sys
import textwrap
import unittest
from cStringIO import StringIO

from byterun.pyvm2 import VirtualMachine, VirtualMachineError


class VmTestCase(unittest.TestCase):

    def assert_ok(self, code):
        """Run `code` in the VM, and in the real Python, and see that they behave the same."""

        code = textwrap.dedent(code)
        code = compile(code, "<string>", "exec")

        if 1:   # Make this "if 1" to see disassembly on failure.
            dis.dis(code)

        old_stdout = sys.stdout
        
        vm_stdout = StringIO()
        sys.stdout = vm_stdout
        vm = VirtualMachine()
        vm.loadCode(code)

        vm_value = vm_exc = None
        try:
            vm_value = vm.run()
        except VirtualMachineError:
            raise
        except Exception, vm_exc:
            pass

        py_stdout = StringIO()
        sys.stdout = py_stdout
        
        py_value = py_exc = None
        try:
            py_value = eval(code)
        except Exception, py_exc:
            pass

        sys.stdout = old_stdout

        self.assert_same_exception(vm_exc, py_exc)
        self.assertEqual(vm_stdout.getvalue(), py_stdout.getvalue())
        self.assertEqual(vm_value, py_value)

    def assert_same_exception(self, e1, e2):
        self.assertEqual(str(e1), str(e2))
        self.assertIs(type(e1), type(e2))

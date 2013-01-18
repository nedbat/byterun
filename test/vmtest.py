"""Testing tools for byterun."""

import dis
import sys
import textwrap
import types
import unittest
from cStringIO import StringIO

from byterun.pyvm2 import VirtualMachine, VirtualMachineError

def dis_code(code):
    """Disassemble `code` and all the code it refers to."""
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            dis_code(const)

    print
    print code
    dis.dis(code)

class VmTestCase(unittest.TestCase):

    def assert_ok(self, code):
        """Run `code` in the VM, and in the real Python, and see that they behave the same."""

        code = textwrap.dedent(code)
        code = compile(code, "<string>", "exec")

        # Print the disassembly so we'll see it if the test fails.
        dis_code(code)

        real_stdout = sys.stdout

        # Run the code through our VM.

        vm_stdout = StringIO()
        sys.stdout = vm_stdout
        vm = VirtualMachine()
        vm.loadCode(code)

        vm_value = vm_exc = None
        try:
            vm_value = vm.run()
        except VirtualMachineError:         # pragma: no cover
            # If the VM code raises an error, show it.
            raise
        except AssertionError:              # pragma: no cover
            # If test code fails an assert, show it.
            raise
        except Exception, vm_exc:
            # Otherwise, keep the exception for comparison later.
            pass
        finally:
            if vm._log:                     # pragma: no branch
                real_stdout.write("-- VM log ----------\n")
                real_stdout.write("\n".join(vm._log))
                real_stdout.write("\n")
            real_stdout.write("-- stdout ----------\n")
            real_stdout.write(vm_stdout.getvalue())

        # Run the code through the real Python interpreter, for comparison.

        py_stdout = StringIO()
        sys.stdout = py_stdout

        py_value = py_exc = None
        try:
            py_value = eval(code)
        except AssertionError:              # pragma: no cover
            raise
        except Exception, py_exc:
            pass

        sys.stdout = real_stdout

        self.assert_same_exception(vm_exc, py_exc)
        self.assertEqual(vm_stdout.getvalue(), py_stdout.getvalue())
        self.assertEqual(vm_value, py_value)

    def assert_same_exception(self, e1, e2):
        """Exceptions don't implement __eq__, check it ourselves."""
        self.assertEqual(str(e1), str(e2))
        self.assertIs(type(e1), type(e2))

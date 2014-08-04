

import dis
import logging
import sys
import types
import unittest


from byterun import abstractvm
from byterun import pycfg
import mock

# It does not accept any styling for several different members for some reason.
# pylint: disable=invalid-name


class MockVM(abstractvm.AbstractVirtualMachine):

  def __init__(self):
    super(MockVM, self).__init__()
    self.load_attr = mock.MagicMock(spec=self.load_attr)


class AbstractVirtualMachineTest(unittest.TestCase):

  def _run_code(self, code, consts, nlocals):
    """Run the given raw byte code.

    Args:
      code: A raw bytecode string to execute.
      consts: The constants for the code.
      nlocals: the number of locals the code uses.
    """
    names = tuple("v" + str(i) for i in xrange(nlocals))
    code = types.CodeType(0,  # argcount
                          nlocals,  # nlocals
                          16,  # stacksize
                          0,  # flags
                          code,  # codestring
                          consts,  # constants
                          names,  # names
                          names,  # varnames
                          "<>",  # filename
                          "",  # name
                          0,  # firstlineno
                          "")  # lnotab
    self.vm.run_code(code)

  def setUp(self):
    self.vm = MockVM()

  def testMagicOperator(self):
    code = pycfg._list_to_string([
        dis.opmap["LOAD_CONST"], 0, 0,  # 0, arg=0
        dis.opmap["LOAD_CONST"], 1, 0,  # 9, arg=1
        dis.opmap["BINARY_ADD"],  # 12
        dis.opmap["STORE_NAME"], 0, 0,  # 13, arg=1
        dis.opmap["LOAD_CONST"], 2, 0,  # 16, arg=2
        dis.opmap["RETURN_VALUE"],  # 19
        ])

    method = mock.MagicMock(spec=(1).__add__)
    self.vm.load_attr.return_value = method
    self._run_code(code, (1, 2, None), 1)
    self.vm.load_attr.assert_called_once_with(1, "__add__")
    method.assert_called_once_with(2)

  def testIter(self):
    code = pycfg._list_to_string([
        dis.opmap["LOAD_CONST"], 0, 0,  # 3, arg=0
        dis.opmap["LOAD_CONST"], 1, 0,  # 6, arg=1
        dis.opmap["LOAD_CONST"], 2, 0,  # 9, arg=2
        dis.opmap["BUILD_LIST"], 3, 0,  # 12, arg=3
        dis.opmap["GET_ITER"],  # 15
        dis.opmap["LOAD_CONST"], 3, 0,  # 26, arg=3
        dis.opmap["RETURN_VALUE"],  # 29
        ])

    method = mock.MagicMock(spec=[1, 2, 3].__iter__)
    self.vm.load_attr.return_value = method
    self._run_code(code, (1, 2, 3, None), 0)
    self.vm.load_attr.assert_called_once_with([1, 2, 3], "__iter__")


class TraceVM(abstractvm.AncestorTraversalVirtualMachine):

  def __init__(self):
    super(TraceVM, self).__init__()
    self.instructions_executed = set()

  def run_instruction(self):
    self.instructions_executed.add(self.frame.f_lasti)
    return super(TraceVM, self).run_instruction()


class AncestorTraversalVirtualMachineTest(unittest.TestCase):

  def setUp(self):
    self.vm = TraceVM()

  srcNestedLoops = """
y = [1,2,3]
z = 0
for x in y:
  for a in y:
    if x:
      z += x*a
"""
  codeNestedLoops = compile(srcNestedLoops, "<>", "exec", 0, 1)

  codeNestedLoopsBytecode = pycfg._list_to_string([
      dis.opmap["LOAD_CONST"], 0, 0,  # 0, arg=0
      dis.opmap["LOAD_CONST"], 1, 0,  # 3, arg=1
      dis.opmap["LOAD_CONST"], 2, 0,  # 6, arg=2
      dis.opmap["BUILD_LIST"], 3, 0,  # 9, arg=3
      dis.opmap["STORE_NAME"], 0, 0,  # 12, arg=0
      dis.opmap["LOAD_CONST"], 3, 0,  # 15, arg=3
      dis.opmap["STORE_NAME"], 1, 0,  # 18, arg=1
      dis.opmap["SETUP_LOOP"], 54, 0,  # 21, dest=78
      dis.opmap["LOAD_NAME"], 0, 0,  # 24, arg=0
      dis.opmap["GET_ITER"],  # 27
      dis.opmap["FOR_ITER"], 46, 0,  # 28, dest=77
      dis.opmap["STORE_NAME"], 2, 0,  # 31, arg=2
      dis.opmap["SETUP_LOOP"], 37, 0,  # 34, dest=74
      dis.opmap["LOAD_NAME"], 0, 0,  # 37, arg=0
      dis.opmap["GET_ITER"],  # 40
      dis.opmap["FOR_ITER"], 29, 0,  # 41, dest=73
      dis.opmap["STORE_NAME"], 3, 0,  # 44, arg=3
      dis.opmap["LOAD_NAME"], 2, 0,  # 47, arg=2
      dis.opmap["POP_JUMP_IF_FALSE"], 41, 0,  # 50, dest=41
      dis.opmap["LOAD_NAME"], 1, 0,  # 53, arg=1
      dis.opmap["LOAD_NAME"], 2, 0,  # 56, arg=2
      dis.opmap["LOAD_NAME"], 3, 0,  # 59, arg=3
      dis.opmap["BINARY_MULTIPLY"],  # 62
      dis.opmap["INPLACE_ADD"],  # 63
      dis.opmap["STORE_NAME"], 1, 0,  # 64, arg=1
      dis.opmap["JUMP_ABSOLUTE"], 41, 0,  # 67, dest=41
      dis.opmap["JUMP_ABSOLUTE"], 41, 0,  # 70, dest=41
      dis.opmap["POP_BLOCK"],  # 73
      dis.opmap["JUMP_ABSOLUTE"], 28, 0,  # 74, dest=28
      dis.opmap["POP_BLOCK"],  # 77
      dis.opmap["LOAD_CONST"], 4, 0,  # 78, arg=4
      dis.opmap["RETURN_VALUE"],  # 81
      ])

  def testEachInstructionOnceLoops(self):
    self.assertEqual(self.codeNestedLoops.co_code,
                     self.codeNestedLoopsBytecode)
    self.vm.run_code(self.codeNestedLoops)
    # The number below are the instruction offsets in the above bytecode.
    self.assertItemsEqual(self.vm.instructions_executed,
                          [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 28, 31, 34, 37,
                           40, 41, 44, 47, 50, 53, 56, 59, 62, 63, 64, 67, 70,
                           73, 74, 77, 78, 81])

  srcDeadCode = """
if False:
  x = 2
raise RuntimeError
x = 42
"""
  codeDeadCode = compile(srcDeadCode, "<>", "exec", 0, 1)

  codeDeadCodeBytecode = pycfg._list_to_string([
      dis.opmap["LOAD_NAME"], 0, 0,  # 0, arg=0
      dis.opmap["POP_JUMP_IF_FALSE"], 15, 0,  # 3, dest=15
      dis.opmap["LOAD_CONST"], 0, 0,  # 6, arg=0
      dis.opmap["STORE_NAME"], 1, 0,  # 9, arg=1
      dis.opmap["JUMP_FORWARD"], 0, 0,  # 12, dest=15
      dis.opmap["LOAD_NAME"], 2, 0,  # 15, arg=2
      dis.opmap["RAISE_VARARGS"], 1, 0,  # 18, arg=1
      dis.opmap["LOAD_CONST"], 1, 0,  # 21, arg=1
      dis.opmap["STORE_NAME"], 1, 0,  # 24, arg=1
      dis.opmap["LOAD_CONST"], 2, 0,  # 27, arg=2
      dis.opmap["RETURN_VALUE"],  # 30
      ])

  def testEachInstructionOnceDeadCode(self):
    self.assertEqual(self.codeDeadCode.co_code,
                     self.codeDeadCodeBytecode)
    try:
      self.vm.run_code(self.codeDeadCode)
    except RuntimeError:
      pass  # Ignore the exception that gets out.
    self.assertItemsEqual(self.vm.instructions_executed,
                          [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30])


if __name__ == "__main__":
  # TODO(ampere): This is just a useful hack. Should be replaced with real
  # argument handling.
  if len(sys.argv) > 1:
    logging.basicConfig(level=logging.DEBUG)
  unittest.main()

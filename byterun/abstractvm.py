"""Classes to ease the abstraction of pyvm2.VirtualMachine.

This module provides 2 classes that provide different kinds of
abstraction. AbstractVirtualMachine abstracts operators and other magic method
uses. AncestorTraversalVirtualMachine changes the execution order of basic
blocks so that each only executes once.
"""

import logging


from byterun import pycfg
from byterun import pyvm2
import six

log = logging.getLogger(__name__)


class AbstractVirtualMachine(pyvm2.VirtualMachine):
    """A base class for abstract interpreters based on VirtualMachine.

    AbstractVirtualMachine replaces the default metacyclic implementation of
    operators and other operations that actually forward to a python magic
    method with a virtual machine level attribute get and a call to the
    returned method.
    """

    def __init__(self):
        super(AbstractVirtualMachine, self).__init__()
        # The key is the instruction suffix and the value is the magic method
        # name.
        binary_operator_name_mapping = dict(
            ADD="__add__",
            AND="__and__",
            DIVIDE="__div__",
            FLOOR_DIVIDE="__floordiv__",
            LSHIFT="__lshift__",
            MODULO="__mod__",
            MULTIPLY="__mul__",
            OR="__or__",
            POWER="__pow__",
            RSHIFT="__rshift__",
            SUBSCR="__getitem__",
            SUBTRACT="__sub__",
            TRUE_DIVIDE="__truediv__",
            XOR="__xor__",
            )
        # Use the above data to generate wrappers for each magic operators. This
        # replaces the original dict since any operator that is not listed here
        # will not work, so it is better to have it cause a KeyError.
        self.binary_operators = dict((op, self.magic_operator(magic))
                                     for op, magic in
                                     binary_operator_name_mapping.iteritems())
        # TODO(ampere): Add support for unary and comparison operators

    def magic_operator(self, name):
        # TODO(ampere): Implement support for r-operators
        def magic_operator_wrapper(x, y):
            return self.call_function(self.load_attr(x, name),
                                      [y], {})
        return magic_operator_wrapper

    @staticmethod
    def reverse_operator_name(name):
        if name.startswith("__"):
            return "__r" + name[2:]
        raise ValueError(
            "Operator name not in a known format: {}".format(name))

    def byte_GET_ITER(self):
        self.push(self.load_attr(self.pop(), "__iter__"))
        self.call_function_from_stack(0, [], {})

    def byte_FOR_ITER(self, jump):
        try:
            self.push(self.load_attr(self.top(), "next"))
            self.call_function_from_stack(0, [], {})
            self.jump(self.frame.f_lasti)
        except StopIteration:
            self.pop()
            self.jump(jump)


class AncestorTraversalVirtualMachine(AbstractVirtualMachine):
    """An abstract interpreter implementing a traversal of basic blocks.

    This class replaces run_frame with a traversal that executes all basic
    blocks in ancestor first order starting with the entry block. This uses
    pycfg.BlockTable.get_ancestors_first_traversal(); see it's documentation for
    more information about the order.

    As the traversal is done there is no attempt to rollback the state, so
    parallel paths in the CFG (even those that cannot be run in the same
    execution) will often see each other's side-effects. Effectively this means
    that the execution of each basic block needs to commute with the execution
    of other blocks it is not ordered with.
    """

    def __init__(self):
        super(AncestorTraversalVirtualMachine, self).__init__()
        self.cfg = pycfg.CFG()

    def frame_traversal_setup(self, frame):
        """Initialize a frame to allow ancestors first traversal.

        Args:
          frame: The execution frame to update.
        """
        frame.block_table = self.cfg.get_block_table(frame.f_code)
        frame.order = frame.block_table.get_ancestors_first_traversal()
        assert frame.f_lasti == 0

    def frame_traversal_next(self, frame):
        """Move the frame instruction pointer to the next instruction.

        This implements the next instruction operation on the ancestors first
        traversal order.

        Args:
          frame: The execution frame to update.

        Returns:
          False if the traversal is done (every instruction in the frames code
          has been executed. True otherwise.
        """
        head = frame.order[0]
        if frame.f_lasti < head.begin or frame.f_lasti > head.end:
            frame.order.pop(0)
            if not frame.order:
                return False
            head = frame.order[0]
            if frame.f_lasti != head.begin:
                log.debug("natural next %d, order next %d",
                          frame.f_lasti, head.begin)
            frame.f_lasti = head.begin
        return True

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        This implementation executes in ancestors first order. See
        pycfg.BlockTable.get_ancestors_first_traversal().

        Args:
          frame: The execution frame.

        Returns:
          The return value of the frame after execution.
        """
        self.push_frame(frame)
        self.frame_traversal_setup(frame)
        while True:
            why = self.run_instruction()
            # TODO(ampere): Store various breaking "why"s so they can be handled
            if not self.frame_traversal_next(frame):
                break
        self.pop_frame()

        # TODO(ampere): We don't really support exceptions.
        if why == "exception":
            six.reraise(*self.last_exception)

        return self.return_value

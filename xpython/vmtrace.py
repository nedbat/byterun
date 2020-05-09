"""A variant of VirtualMachine that adds a callback.
This can be used in a debugger or profiler.
"""

import six
from xdis import PYTHON_VERSION, IS_PYPY
from xpython.vm import (
    PyVM,
    PyVMError,
)
from xpython.pyobj import traceback_from_frame

import logging
log = logging.getLogger(__name__)

class PyVMTraced(PyVM):
    def __init__(
            self, callback, python_version=PYTHON_VERSION, is_pypy=IS_PYPY, vmtest_testing=False,
    ):
        super().__init__(python_version, is_pypy, vmtest_testing)
        self.callback = callback
        # TODO:
        # * add events of interest
        # * add offset breakpoints
        # * add line number breakopints
        # * add function breakpoints

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        """
        self.push_frame(frame)
        code = self.f_code = self.frame.f_code
        self.linestarts = dict(self.opc.findlinestarts(self.f_code, dup_lines=True))
        self.callback("call", 0, 'CALL', None, self)

        opoffset = 0
        while True:
            byteName, arguments, opoffset, line_number = self.parse_byte_and_args()
            self.callback("step-instruction", opoffset, byteName, arguments, self)

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = self.dispatch(byteName, arguments, opoffset)
            if why == "exception":
                # Deal with exceptions encountered while executing the op.
                if not self.in_exception_processing:
                    self.last_traceback = traceback_from_frame(self.frame)
                    self.in_exception_processing = True

            if why == "reraise":
                why = "exception"

            if why != "yield":
                while why and frame.block_stack:
                    # Deal with any block management we need to do.
                    why = self.manage_block_stack(why)

            if why:
                break

        # TODO: handle generator exception state

        event_type = "exception" if why == "exception" else "return"
        self.callback(event_type, opoffset, byteName, arguments, self)
        self.pop_frame()

        if why == "exception":
            if self.last_exception and self.last_exception[0]:
                six.reraise(*self.last_exception)
            else:
                raise PyVMError("Borked exception recording")
            # if self.exception and .... ?
            # log.error("Haven't finished traceback handling, nulling traceback information for now")
            # six.reraise(self.last_exception[0], None)

        self.in_exception_processing = False
        return self.return_value

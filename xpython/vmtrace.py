"""A variant of VirtualMachine that adds a callback.
This can be used in a debugger or profiler.
"""

import six
from xdis import PYTHON_VERSION, IS_PYPY
from xpython.vm import (
    byteint,
    PyVM,
    PyVMError,
)
from xpython.pyobj import traceback_from_frame

import logging

log = logging.getLogger(__name__)

PyVMEVENT_INSTRUCTION = 1
PyVMEVENT_LINE = 2
PyVMEVENT_CALL = 4
PyVMEVENT_RETURN = 8
PyVMEVENT_EXCEPTION = 16
PyVMEVENT_YIELD = 32


class PyVMTraced(PyVM):
    def __init__(
        self,
        callback,
        python_version=PYTHON_VERSION,
        is_pypy=IS_PYPY,
        vmtest_testing=False,
        event_flags=31,
    ):
        super().__init__(python_version, is_pypy, vmtest_testing)
        self.callback = callback
        self.event_flags = event_flags

        # TODO:
        # * add events of interest
        # * add offset breakpoints
        # * add line number breakopints
        # * add function breakpoints

    def run_frame(self, frame):
        """Run a frame until it returns (somehow).

        Exceptions are raised, the return value is returned.

        """
        if frame.f_lasti == -1:
            # We were started new, not yielded back from
            frame.f_lasti = 0
            frame.fallthrough = (
                False  # Don't increment before fetching next instruction
            )
            byteCode = None
            last_i = frame.f_back.f_lasti if frame.f_back else -1
            self.push_frame(frame)
            if self.event_flags & PyVMEVENT_CALL:
                self.callback("call", last_i, "CALL", byteCode, frame.f_lineno, [], self)
                pass
        else:
            byteCode = byteint(frame.f_code.co_code[frame.f_lasti])
            self.push_frame(frame)
            if self.event_flags & PyVMEVENT_YIELD:
                self.callback("yield", opoffset, byteName, "YIELD_VALUE", frame.f_lineno, [], self)
                pass
            # byteCode == opcode["YIELD_VALUE"]?

        self.linestarts = dict(self.opc.findlinestarts(frame.f_code, dup_lines=True))

        opoffset = 0
        while True:

            (
                byteName,
                byteCode,
                intArg,
                arguments,
                opoffset,
                line_number,
            ) = self.parse_byte_and_args(byteCode)

            if log.isEnabledFor(logging.INFO):
                self.log(byteName, intArg, arguments, opoffset, line_number)

            if line_number is not None and self.event_flags & (
                PyVMEVENT_LINE | PyVMEVENT_INSTRUCTION
            ):
                self.callback("line", opoffset, byteName, byteCode, line_number, arguments, self)
            elif self.event_flags & PyVMEVENT_INSTRUCTION:
                self.callback("instruction", opoffset, byteName, byteCode, line_number, arguments, self)

            # When unwinding the block stack, we need to keep track of why we
            # are doing it.
            why = self.dispatch(byteName, intArg, arguments, opoffset, line_number)
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

        if why == "exception":
            if self.event_flags & PyVMEVENT_EXCEPTION:
                self.callback(
                    "exception", opoffset, byteName, byteCode, line_number, self.last_exception, self
                )
            elif self.event_flags & PyVMEVENT_RETURN:
                self.callback("return", opoffset, byteName, byteCode, line_number, self.return_value, self)
            pass

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
        if self.event_flags & PyVMEVENT_RETURN:
            self.callback("return", opoffset, byteName, byteCode, line_number, self.return_value, self)

        return self.return_value

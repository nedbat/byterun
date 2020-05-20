|TravisCI| |CircleCI|

x-python
--------

This is a CPython bytecode interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Experiment with additional opcodes, or ways to change the run-time environment
* Use as a sandboxed environment for trying pieces of execution
* Have one Python program that runs multiple versions of Python bytecode.
* Use in a dynamic fuzzer or in coholic execution for analysis

The sandboxed environment in a debugger I find interesting. Since
there is a separate execution, and traceback stack, inside a debugger
you can try things out in the middle of a debug session without
effecting the real execution. On the other hand if a sequence of
executions works out, it is possible to copy this (under certain
circumstances) back into CPython's execution stack.

Going the other way, I have hooked in `trepan3k
<https://pypi.python.org/pypi/trepan3k>`_ into this interpreter so you
have a pdb/gdb like debugger also with the ability to step bytecode
instructions.

I may also experiment with faster ways to support trace callbacks such
as those used in a debugger. In particular I may add a `BREAKPOINT`
instruction to support fast breakpoints and breakpointing on a
particular instruction that doesn't happen to be on a line boundary.

Although this is far in the future, suppose you to add a race
detector? It might be easier to prototype it in Python here. (This
assumes the interpreter supports threading well, I suspect it doesn't)

Another unexplored avenue implied above is mixing interpretation and
direct CPython execution. In fact, there are bugs so this happens
right now, but it will be turned into a feature. Some functions or
classes you may want to not run under a slow interpreter while others
you do want to run under the interpreter.


Examples:
+++++++++

What to know instructions get run when you write some simple code?
Try this:

::

   $ xpython -vc "x, y = 2, 3; x **= y"
   INFO:xpython.vm:L. 1   @  0: LOAD_CONST (2, 3)
   INFO:xpython.vm:       @  2: UNPACK_SEQUENCE 2
   INFO:xpython.vm:       @  4: STORE_NAME x
   INFO:xpython.vm:       @  6: STORE_NAME y
   INFO:xpython.vm:L. 1   @  8: LOAD_NAME x
   INFO:xpython.vm:       @ 10: LOAD_NAME y
   INFO:xpython.vm:       @ 12: INPLACE_POWER
   INFO:xpython.vm:       @ 14: STORE_NAME x
   INFO:xpython.vm:       @ 16: LOAD_CONST None
   INFO:xpython.vm:       @ 18: RETURN_VALUE

Option `-c` is the same as Python's flag (program passed in as string)
and `-v` is also analogus Python's flag. Here, it shows the bytecode
instructions run.

Want the execution stack stack and block stack in addition? Add another `v`:

::

   $ xpython -vvc "x, y = 2, 3; x **= y"

   DEBUG:xpython.vm:make_frame: code=<code object <module> at 0x7f7acd353420, file "<string x, y = 2, 3; x **= y>", line 1>, callargs={}, f_globals=(<class 'dict'>, 140165406216272), f_locals=(<class 'NoneType'>, 94599533407680)
   DEBUG:xpython.vm:<Frame at 0x7f7acd322650: '<string x, y = 2, 3; x **= y>':1 @-1>
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:L. 1   @  0: LOAD_CONST (2, 3) <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [(2, 3)]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  2: UNPACK_SEQUENCE 2 <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [3, 2]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  4: STORE_NAME x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [3]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  6: STORE_NAME y <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:L. 1   @  8: LOAD_NAME x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [2]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 10: LOAD_NAME y <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [2, 3]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 12: INPLACE_POWER  <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [8]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 14: STORE_NAME x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 16: LOAD_CONST None <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [None]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 18: RETURN_VALUE  <module> in <string x, y = 2, 3; x **= y>:1


Want to see this colorized in a terminal? Use this via `trepan-xpy`: |assign example|

Suppose you have Python 2.5 bytecode (or some other bytecode) for
this, but you are running Python 3.7?

::

   $ xpython -vc "x = 6 if __name__ != '__main__' else 10"
   INFO:xpython.vm:L. 1   @  0: LOAD_CONST (2, 3)
   INFO:xpython.vm:       @  3: UNPACK_SEQUENCE 2
   INFO:xpython.vm:       @  6: STORE_NAME x
   INFO:xpython.vm:       @  9: STORE_NAME y
   INFO:xpython.vm:L. 2   @ 12: LOAD_NAME x
   INFO:xpython.vm:       @ 15: LOAD_NAME y
   INFO:xpython.vm:       @ 18: INPLACE_POWER
   INFO:xpython.vm:       @ 19: STORE_NAME x
   INFO:xpython.vm:       @ 22: LOAD_CONST None
   INFO:xpython.vm:       @ 25: RETURN_VALUE

Not much has changed here, other then the fact that that in after 3.6 instructions are two bytes instead of 1-3 bytes.

The above examples show straight-line code, so you see all of the instructions. But don't confuse this with a disassembler like `pydisasm` from `xdis`.
The below example, with conditional branching example makes this more clear:
::

    $ xpython -vc "x = 6 if __name__ != '__main__' else 10"
    INFO:xpython.vm:L. 1   @  0: LOAD_NAME __name__
    INFO:xpython.vm:       @  2: LOAD_CONST __main__
    INFO:xpython.vm:       @  4: COMPARE_OP !=
    INFO:xpython.vm:       @  6: POP_JUMP_IF_FALSE 12
    INFO:xpython.vm:       @ 12: LOAD_CONST 10
    INFO:xpython.vm:       @ 14: STORE_NAME x
    INFO:xpython.vm:       @ 16: LOAD_CONST None
    INFO:xpython.vm:       @ 18: RETURN_VALUE

Want even more status and control? See `trepan-xpy <https://github.com/rocky/trepan-xpy>`_.

Status:
+++++++

Currently bytecode from Python versions 3.7 - 3.2, and 2.7 - 2.5 are
supported. Extending to 3.8 and beyond is on hold until there is more
interest, I get help, I need or there is or funding,

Whereas *Byterun* was a bit loose in accepting bytecode opcodes that
is invalid for particular Python but may be valid for another;
*x-python* is more stringent. This has pros and cons. On the plus side
*Byterun* might run certain Python 3.4 bytecode because the opcode
sets are similar. However starting with Python 3.5 and beyond the
likelihood happening becomes vanishingly small. And while the
underlying opcode names may be the same, the semantics of the
operation may change subtely. See for example
https://github.com/nedbat/byterun/issues/34.

Internally Byterun needs the kind of overhaul we have here to be able
to scale to support bytecode for more Pythons, and to be able to run
bytecode across different versions of Python. Specifically, you can't
rely on Python's `dis <https://docs.python.org/3/library/dis.html>`_
module if you expect to expect to run a bytecode other than the
bytecode that the interpreter is running.

In *x-python* there is a clear distinction between the version being
interpreted and the version of Python that is running. There is
tighter control of opcodes and an opcode's implementation is kept for
each Python version. So we'll warn early when something is
invalid. You can run 3.3 bytecode using Python 3.7 (largely).

The "largely" part is because the interpreter has always made use of
Python builtins. When a Python version running the interperter matches a
supported bytecode close enough, the interpreter can (and does) make use
interpreter internals. For example, built-in functions like `range()`
are supported this way.

Running 2.7 bytecode on 3.x is sometimes not possible when the
portions of the runtime and internal libraries are too different.

Over time more of Python's internals need to be get added so we have
better cross-version compatability. More difficult is running later
byecode from earlier Python versions. The challenge here is that many
new features like asynchronous I/O and concurrency primatives are not
in the older versions and may not easily be simulated. However that
too is a possibility if there is interest.

You can run many of the tests that Python uses to test itself, (and I
do!) and those work. Right now this program works best on Python up to
3.4 when life in Python was much simpler. It runs over 300 in Python's
test suite for itself without problems.

Moving back and forward from 3.4 things worse. Python 3.5 is pretty
good. Python 3.6 and 3.7 is okay but need work.


History
+++++++

This is a fork of *Byterun.* which is a pure-Python implementation of
a Python bytecode execution virtual machine.  Net Batchelder started
it (based on work from Paul Swartz) to get a better understanding of
bytecodes so he could fix branch coverage bugs in coverage.py.

.. |CircleCI| image:: https://circleci.com/gh/rocky/x-python.svg?style=svg
    :target: https://circleci.com/gh/rocky/x-python
.. |TravisCI| image:: https://travis-ci.org/rocky/x-python.svg?branch=master
		 :target: https://travis-ci.org/rocky/x-python

.. |assign example| image:: https://github.com/rocky/x-python/blob/master/screenshots/trepan-xpy-assign.gif

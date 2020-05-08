|TravisCI| |CircleCI|

x-python
--------

This is a CPython bytecode interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Use as a sandboxed environment for trying pieces of execution
* Have one Python program that runs multiple versions of Python bytecode.
  For a number of things you can Python 2.5 or 2.6 bytecode from inside Python 3.7;
  No need to install Python 2.5 or 2.6!
* Use in a dynamic fuzzer or in coholic execution for analysis

The sandboxed environment in a debugger I find interesting. Since
there is a separate execution, and traceback stack, inside a debugger
you can try things out in the middle of a debug session without
effecting the real execution. On the other hand if a sequence of
executions works out, it is possible to copy this (under certain
circumstances) back into CPython's execution stack.

Going the other way, I may at some point hook in `my debugger
<https://pypi.python.org/pypi/trepan3k>`_ into this interpreter and then
you'll have a conventional pdb/gdb like debugger also with the ability
to step bytecode instructions.

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
   INFO:xpython.pyvm2:Line    1,   0: LOAD_CONST (2, 3)
   INFO:xpython.pyvm2:             2: UNPACK_SEQUENCE 2
   INFO:xpython.pyvm2:             4: STORE_NAME 'x'
   INFO:xpython.pyvm2:             6: STORE_NAME 'y'
   INFO:xpython.pyvm2:             8: LOAD_NAME 'x'
   INFO:xpython.pyvm2:            10: LOAD_NAME 'y'
   INFO:xpython.pyvm2:            12: INPLACE_POWER
   INFO:xpython.pyvm2:            14: STORE_NAME 'x'
   INFO:xpython.pyvm2:            16: LOAD_CONST None
   INFO:xpython.pyvm2:            18: RETURN_VALUE

Option `-c` is the same as Python's flag (program passed in as string)
and `-v` is also analogus Python's flag. Here, it shows the bytecode
instructions run.

Want the execution stack stack and block stack in addition? Add another `v`:

::

   $ xpython -vvc "x, y = 2, 3; x **= y"
   DEBUG:xpython.pyvm2:make_frame: code=<code object <module> at 0x7f33d1cf01e0, file "<string x, y = 2, 3; x **= y>", line 1>, callargs={}, f_globals=(<class 'dict'>, 139860540041568), f_locals=(<class 'NoneType'>, 94796399066560)
   DEBUG:xpython.pyvm2:<Frame at 0x7f33d135ef50: '<string x, y = 2, 3; x **= y>' @ 1>
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:Line    1,   0: LOAD_CONST (2, 3)
   DEBUG:xpython.pyvm2:  frame.stack: [(2, 3)]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             2: UNPACK_SEQUENCE 2
   DEBUG:xpython.pyvm2:  frame.stack: [3, 2]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             4: STORE_NAME 'x'
   DEBUG:xpython.pyvm2:  frame.stack: [3]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             6: STORE_NAME 'y'
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             8: LOAD_NAME 'x'
   DEBUG:xpython.pyvm2:  frame.stack: [2]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            10: LOAD_NAME 'y'
   DEBUG:xpython.pyvm2:  frame.stack: [2, 3]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            12: INPLACE_POWER
   DEBUG:xpython.pyvm2:  frame.stack: [8]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            14: STORE_NAME 'x'
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            16: LOAD_CONST None
   DEBUG:xpython.pyvm2:  frame.stack: [None]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            18: RETURN_VALUE


The above showed straight-line code, so you see all of the instructions. But don't confuse this with a disassembler like `pydisasm` from `xdis`.
The below example, with conditional branching example makes this more clear:

::

   $ xpython -vvc "x = 6 if __name__ != '__main__' else 10"
   DEBUG:xpython.pyvm2:make_frame: code=<code object <module> at 0x7f2dd0d2f150, file "<string x = 6 if __name__ !=>", line 1>, callargs={}, f_globals=(<class 'dict'>, 139834753714688), f_locals=(<class 'NoneType'>, 94349724270016)
   DEBUG:xpython.pyvm2:<Frame at 0x7f2dd039ded0: '<string x = 6 if __name__ !=>' @ 1>
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:Line    1,   0: LOAD_NAME '__name__'
   DEBUG:xpython.pyvm2:  frame.stack: ['__main__']
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             2: LOAD_CONST '__main__'
   DEBUG:xpython.pyvm2:  frame.stack: ['__main__', '__main__']
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             4: COMPARE_OP 3
   DEBUG:xpython.pyvm2:  frame.stack: [False]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:             6: POP_JUMP_IF_FALSE 12
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            12: LOAD_CONST 10
   DEBUG:xpython.pyvm2:  frame.stack: [10]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            14: STORE_NAME 'x'
   DEBUG:xpython.pyvm2:  frame.stack: []
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            16: LOAD_CONST None
   DEBUG:xpython.pyvm2:  frame.stack: [None]
   DEBUG:xpython.pyvm2:  blocks     : []
   INFO:xpython.pyvm2:            18: RETURN_VALUE

Status:
+++++++

Currently only Python 2.5 - 2.7, and 3.2 - 3.7 bytecode is supported.
Until there is more interest or I get support or funding, I am not
contemplating expanding to 3.8 and beyond for a while.

A shout out to `xdis <https://pypi.python.org/pypi/xdis>`_ which has
made cross version interpretation and expanding to other versions
easier.

Whereas *Byterun* was a bit loose in accepting bytecode opcodes that
is invalid for particular Python but may be valid for another;
*x-python* is more stringent. This has pros and cons. On the plus side
*Byterun* might run certain Python 3.4 bytecode because the opcode
sets are similar. However starting with Python 3.5 and beyond the
likelihood gets much less because, while the underlying opcode names
may be the same, the semantics of the operation may change
subtely. See for example
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

Currently running 2.7 bytecode on 3.x is often not feasible since the
runtime and internal libraries used like `inspect` are too different.

Over time more of Python's internals may get added so we have better
cross-version compatability, so that is a possibility. Harder is to
run later byecode from earlier Python versions. The callenge here is
that many new features like asynchronous I/O and concurrency
primatives are not in the older versions and may not easily be
simulated. However that too is a possibility if there is interest.

You can run many of the tests that Python uses to test itself, and
those work. Right now this program works best on Python up to 3.4 when
life in Python was much simpler. It runs over 300 in Python's test
suite for itself without problems.

Moving back and forward from 3.4 things worse. Python 3.5 is pretty
good. Python 3.6 and 3.7 is okay but needs work.


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

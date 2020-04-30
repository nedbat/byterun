|buildstatus|

xpython
--------

This is a C Python interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Use as a sandboxed environment inside a debugger for trying pieces of execution
* Have one Python program that runs multiple versions of Python bytecode.
  For example running Python 2.6 bytecode from Python 3.7.
  No need to install Python 2.6!

The sandboxed sandboxed environment in a debugger I find
interesting. Since there is a separate execution, and traceback stack,
inside a debugger you can try things out in the middle of a debug
session without effecting the real execution. On the other hand if a
sequence of executions works out, it is possible to copy this (under
certain circumstances) back into CPython's execution stack.

Going the other way, I may at some point hook in my debugger into this
interpreter and then you'll have a conventional pdb/gdb like debugger
also with the ability to step bytecode instructions.

Status:
+++++++

Currently only Python 2.6, 2.7, 3.3 and Python 3.3 bytecode is well
understood.  Other versions will start to appear with the help of
`xdis`.

Whereas *Byterun* was a bit loose in accepting bytecode opcodes that
is invalid for particular Python but may be valid for another;
*xpython* is more stringent. This has pros and cons. On the plus side
*Byterun* might run certain Python 3.4 bytecode because the opcode
sets are similar. However starting with Python 3.5 and beyond the
likelihood gets much less because, while the underlying opcode names
may be the same, the semantics of the operation may change
subtely. See for example
https://github.com/nedbat/byterun/issues/34.

Internally Byterun needs the kind of overhaul we have here to be able
to scale to support bytecode for more Pythons, and to be able to run
that bytecode across different versions of Python. Specifically, you
can't use Python's `dis` module, and a clearer distinction between the
version being interpreter and the version of Python running needs to
be made.

With `xpython`, tighter control of opcodes and an opcode's
implementation is kept for each Python version. So we'll warn early
when something is invalid. So in contrast to *Byterun* you can run 3.3
bytecode using Python 3.7 (largely).

The "largely" part is because the interpreter has always made use of
Python builtins. When a Python version running the interperter matches a
supported bytecode close enough, the interpreter can (and does) make use
interpreter internals. For example, built-in functions like `range()`
are supported this way.

However running 2.7 bytecode on 3.x is often not feasible since the
runtime and internal libraries used like `inspect` are too different.

I would say this is more than a a simple toy interpreter, but it will
never be as complete as CPython or PyPy.


History
+++++++

This is a fork of *Byterun.* which is a pure-Python implementation of
a Python bytecode execution virtual machine.  Net Batchelder started
it (based on work from Paul Swartz) to get a better understanding of
bytecodes so he could fix branch coverage bugs in coverage.py.

.. |buildstatus| image:: https://circleci.com/gh/rocky/xpython.svg?style=svg
    :target: https://circleci.com/gh/rocky/xpython

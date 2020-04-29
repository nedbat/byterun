xpython
--------

This is a C Python interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Use as a sandboxed environment inside a debugger for trying pieces of execution
* Have one Python program that can run several versions of Python Bytecode

The sandboxed sandboxed environment in a debugger may be
interesting. Since there is a separate execution, and traceback stack,
inside a debugger you can try things out in the middle of a debug
session without effecting the real execution. On the other hand if a
sequence of executions works out, it is possible to copy this
(under certain circumstances) back into CPython's execution stack.

Going the other way, I may at some point hook in my debugger into this
interpreter and then you'll have a conventional pdb/gdb like debugger
also with the ability to step bytecode instructions.

Status:
+++++++

Currently only Python 3.3 and Python 2.7 bytecode is understood.
After a refactor of the bytecode mechanism, I expect other versions will
start to appear with the help of `xdis`.

In contrast to *Byterun* from which this has been forked, described
below, with certain caveats, this interpreter is able to run on Python
versions outside of the one that it is interpreting, i.e. 3.3 or 2.7.

In particular, you can run 3.3 bytecode using Python 3.7. However running
2.7 bytecode on 3.x is not feasible.

I would say this is more than a a simple toy interpreter, but it will
never be as complete as CPython or PyPy. Note that when Python version
running the interperter matches a supported bytecode, the interpreter
can (and does) make use interpreter internals. For example, built-in
functions like `range()` are supported this way.


History
+++++++

This is a fork of *Byterun.* which is a pure-Python implementation of
a Python bytecode execution virtual machine.  Net Batchelder started
it (based on work from Paul Swartz) to get a better understanding of
bytecodes so he could fix branch coverage bugs in coverage.py.

|TravisCI| |CircleCI| |Pypi Installs| |Latest Version| |Supported Python Versions|

x-python
--------

This is a CPython bytecode interpreter written Python.

You can use this to:

* Learn about how the internals of CPython works since this models that
* Experiment with additional opcodes, or ways to change the run-time environment
* Use as a sandboxed environment for trying pieces of execution
* Have one Python program that runs multiple versions of Python bytecode.
* Use in a dynamic fuzzer or in coholic execution for analysis

The ability to run Python bytecode as far back as 2.4 from Python 3.7
I find pretty neat. (Even more could easily be added).

Also, The sandboxed environment in a debugger I find
interesting. (Note: currently environments are not sandboxed that
well, but I am working towards that.)

Since there is a separate execution, and traceback stack,
inside a debugger you can try things out in the middle of a debug
session without effecting the real execution. On the other hand if a
sequence of executions works out, it is possible to copy this (under
certain circumstances) back into CPython's execution stack.

Going the other way, I have hooked in `trepan3k
<https://pypi.python.org/pypi/trepan3k>`_ into this interpreter so you
have a pdb/gdb like debugger also with the ability to step bytecode
instructions.

I may also experiment with faster ways to support trace callbacks such
as those used in a debugger. In particular I may add a ``BREAKPOINT``
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
   INFO:xpython.vm:       @  4: STORE_NAME (2) x
   INFO:xpython.vm:       @  6: STORE_NAME (3) y
   INFO:xpython.vm:L. 1   @  8: LOAD_NAME x
   INFO:xpython.vm:       @ 10: LOAD_NAME y
   INFO:xpython.vm:       @ 12: INPLACE_POWER (2, 3)
   INFO:xpython.vm:       @ 14: STORE_NAME (8) x
   INFO:xpython.vm:       @ 16: LOAD_CONST None
   INFO:xpython.vm:       @ 18: RETURN_VALUE (None)

Option ``-c`` is the same as Python's flag (program passed in as string)
and ``-v`` is also analogus Python's flag. Here, it shows the bytecode
instructions run.

Note that the disassembly above in the dynamic trace above gives a
little more than what you'd see from a static disassembler from
Python's ``dis`` module. In particular, the ``STORE_NAME``
instructions show the *value* that is store, e.g. "2" at instruction
offset 4 into name ``x``. Similarly ``INPLACE_POWER`` shows the operands, 2 and 3, which is how the value
8 is derived as the operand of the next instruction, ``STORE_NAME``.

Want more like the execution stack stack and block stack in addition? Add another `v`:

::

   $ xpython -vvc "x, y = 2, 3; x **= y"

   DEBUG:xpython.vm:make_frame: code=<code object <module> at 0x7f8018507db0, file "<string x, y = 2, 3; x **= y>", line 1>, callargs={}, f_globals=(<class 'dict'>, 140188140947488), f_locals=(<class 'NoneType'>, 93856967704000)
   DEBUG:xpython.vm:<Frame at 0x7f80184c1e50: '<string x, y = 2, 3; x **= y>':1 @-1>
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:L. 1   @  0: LOAD_CONST (2, 3) <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [(2, 3)]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  2: UNPACK_SEQUENCE 2 <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [3, 2]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  4: STORE_NAME (2) x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [3]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @  6: STORE_NAME (3) y <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:L. 1   @  8: LOAD_NAME x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [2]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 10: LOAD_NAME y <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [2, 3]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 12: INPLACE_POWER (2, 3)  <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [8]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 14: STORE_NAME (8) x <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: []
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 16: LOAD_CONST None <module> in <string x, y = 2, 3; x **= y>:1
   DEBUG:xpython.vm:  frame.stack: [None]
   DEBUG:xpython.vm:  blocks     : []
   INFO:xpython.vm:       @ 18: RETURN_VALUE (None)  <module> in <string x, y = 2, 3; x **= y>:1


Want to see this colorized in a terminal? Use this via ``trepan-xpy -x``:
|trepan-xpy-example|

Suppose you have Python 2.4 bytecode (or some other bytecode) for
this, but you are running Python 3.7?

::

   $ xpython -v test/examples/assign-2.4.pyc
   INFO:xpython.vm:L. 1   @  0: LOAD_CONST (2, 3)
   INFO:xpython.vm:       @  3: UNPACK_SEQUENCE 2
   INFO:xpython.vm:       @  6: STORE_NAME (2) x
   INFO:xpython.vm:       @  9: STORE_NAME (3) y
   INFO:xpython.vm:L. 2   @ 12: LOAD_NAME x
   INFO:xpython.vm:       @ 15: LOAD_NAME y
   INFO:xpython.vm:       @ 18: INPLACE_POWER (2, 3)
   INFO:xpython.vm:       @ 19: STORE_NAME (8) x
   INFO:xpython.vm:       @ 22: LOAD_CONST None
   INFO:xpython.vm:       @ 25: RETURN_VALUE (None)

Not much has changed here, other then the fact that that in after 3.6 instructions are two bytes instead of 1- or 3-byte instructions.

The above examples show straight-line code, so you see all of the instructions. But don't confuse this with a disassembler like `pydisasm` from `xdis`.
The below example, with conditional branching example makes this more clear:
::

    $ xpython -vc "x = 6 if __name__ != '__main__' else 10"
    INFO:xpython.vm:L. 1   @  0: LOAD_NAME __name__
    INFO:xpython.vm:       @  2: LOAD_CONST __main__
    INFO:xpython.vm:       @  4: COMPARE_OP ('__main__', '__main__') !=
    INFO:xpython.vm:       @  6: POP_JUMP_IF_FALSE 12
                                                   ^^ Note jump below
    INFO:xpython.vm:       @ 12: LOAD_CONST 10
    INFO:xpython.vm:       @ 14: STORE_NAME (10) x
    INFO:xpython.vm:       @ 16: LOAD_CONST None
    INFO:xpython.vm:       @ 18: RETURN_VALUE (None)

Want even more status and control? See `trepan-xpy <https://github.com/rocky/trepan-xpy>`_.

Status:
+++++++

Currently bytecode from Python versions 3.7 - 3.2, and 2.7 - 2.4 are
supported. Extending to 3.8 and beyond is on hold until there is more
interest, I get help, I need or there is or funding.

*Byterun*, from which this was based on, is awesome. But it cheats in
subtle ways.

Want to write a very small interpreter using CPython?

::

   # get code somehow
   exec(code)

This cheats in kind of a gross way, but this the kind of cheating goes
on in *Byterun* in a more subtle way. As in the example above which
relies on built-in function ``exec`` to do all of the work, *Byterun*
relies on various similar sorts of built-in functions to support
opcode interpretation. In fact, if the code you were *interpreting*
was the above, *Byterun* would use its built-in function for running
code inside the `exec` function call, so all of the bytecode that gets
run inside code inside *code* would not seen for interpretation.

Also, built-in functions like `exec`, and other built-in modules have
an effect in the interpreter namespace.  So the two namespaces then
get intermingled.

One example of this that has been noted is for ``import``. See
https://github.com/nedbat/byterun/issues/26.  But there are others
cases as well.  While we haven't addressed the ``import`` issue
mentioned in issue 26, we have addressed similar kinds of issues like
this.

Some built-in functions and the ``inpsect`` module require built-in
types like cell, traceback, or frame objects, and they can't use the
corresponding interpreter classes. Here is an example of this in
*Byterun*: class ``__init__`` functions don't get traced into, because
the built-in function ``__build_class__`` is relied on. And
``__build_class__`` needs a native function, not an
interpreter-traceable function. See
https://github.com/nedbat/byterun/pull/20.

Also *Byterun* is loose in accepting bytecode opcodes that is invalid
for particular Python but may be valid for another. I suppose this is
okay since you don't expect invalid opcodes appearing in valid
bytecode. It can however accidentally or erronously appear code that
has been obtained via some sort of extraction process, when the
extraction process isn't accruate.

In contrast to *Byterun*, *x-python* is more stringent what opcodes it
accepts.

Byterun needs the kind of overhaul we have here to be able to scale to
support bytecode for more Pythons, and to be able to run bytecode
across different versions of Python. Specifically, you can't rely on
Python's `dis <https://docs.python.org/3/library/dis.html>`_ module if
you expect to run a bytecode other than the bytecode that the
interpreter is running, or run newer "wordcode" bytecode on a
"byte"-oriented byteocde, or vice versa.

In contrast, *x-python* there is a clear distinction between the
version being interpreted and the version of Python that is
running. There is tighter control of opcodes and an opcode's
implementation is kept for each Python version. So we'll warn early
when something is invalid. You can run bytecode back to Python 2.4
using Python 3.7 (largely), which is amazing give that 3.7's native
byte code is 2 bytes per instruction while 2.4's is 1 or 3 bytes per
instruction.

The "largely" part is, as mentioned above, because the interpreter has
always made use of Python builtins and libraries, and for the most
part these haven't changed very much. Often, since many of the
underlying builtins are the same, the interpreter can (and does) make
use interpreter internals. For example, built-in functions like
``range()`` are supported this way.

So interpreting bytecode from a newer Python release than the release
the Python interpreter is using, is often doable too. Even though
Python 2.7 doesn't support keyword-only arguments or format strings,
it can still interpret bytecode created from using these constructs.

That's possible here because these specific features are more
syntactic sugar rather than extensions to the runtime. For example,
format strings basically map down to using the ``format()`` function
which is available on 2.7.

But new features like asynchronous I/O and concurrency primitives are not
in the older versions. So those need to be simulated, and that too is a
possibility if there is interest or support.

You can run many of the tests that Python uses to test itself, and I
do! And most of those work. Right now this program works best on Python up to
3.4 when life in Python was much simpler. It runs over 300 in Python's
test suite for itself without problems. For Python 3.6 the number
drops down to about 237; Python 3.7 is worse still.


History
+++++++

This is a fork of *Byterun.* which is a pure-Python implementation of
a Python bytecode execution virtual machine.  Ned Batchelder started
it (based on work from Paul Swartz) to get a better understanding of
bytecodes so he could fix branch coverage bugs in coverage.py.

.. |CircleCI| image:: https://circleci.com/gh/rocky/x-python.svg?style=svg
    :target: https://circleci.com/gh/rocky/x-python
.. |TravisCI| image:: https://travis-ci.org/rocky/x-python.svg?branch=master
		 :target: https://travis-ci.org/rocky/x-python

.. |trepan-xpy-example| image:: https://github.com/rocky/x-python/blob/master/screenshots/trepan-xpy-assign.gif
.. |Latest Version| image:: https://badge.fury.io/py/x-python.svg
		 :target: https://badge.fury.io/py/x-python
.. |PyPI Installs| image:: https://pepy.tech/badge/x-python/month
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/x-python.svg

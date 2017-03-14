Byterun
-------



Byterun is a python interpreter written in just 1451 lines of Python.
Byterun's goal is to clearly explain Python's design. 
If you want to better understand Python, or you are not quite sure how something in cPYthon works, then Byterun is  a great place to start. 
Byterun has proven very useful to a number of different projects, `including one by Google <https://github.com/nedbat/byterun/pull/12>`_.  

By interpreter we mean a code execution virtual 
machine.  The Python compiler converts python source code into Python bytecode.  The code execution virtual machine then executes that bytecode.   

There are a number of python virtual machines.  Most Python developers use cPython.  cPython includes a virtual machine written in C.  Yes it runs Python very fast, but it is a large code base, and difficult to understand.  Much better to start by studying Byterun.  Then you can move onto cPython.   

If you are interested in Byterun,  the first step is to read the 
excellent introductory article on Byterun written by Alison 
Kaptur.  `A Python Interpreter written in Python <http://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html>`_

If you are not sure what a stack machine is, you might even start  
with `the Wikipedia article on stack machines. <https://en.wikipedia.org/wiki/Stack_machine>`_

After understanding Alison's Byterun  article, you should be able to make sense of  
`the source code for this repository </byterun>`_  
And from there you can move onto studying  cPython, or PyPy, or Jython. 

In the process, you
will certainly need to refer to `the list of Python bytecodes <https://docs.python.org/2.4/lib/bytecodes.html>`_
 
And as you get deeper into the code, you will need to refer to the `Python Execution Model <https://docs.python.org/3/reference/executionmodel.html>`_

We invite you to join this community.  What do you want to do with Byterun?  Do you have any questions?

 
History
-------

`Ned Batchelder <https://nedbatchelder.com/>`_,
`started Byterun <https://nedbatchelder.com/blog/201301/byterun_and_making_cells.html>`_ so that he could  get a better understanding of bytecodes so that he could fix branch coverage bugs in `coverage.py <https://github.com/nedbat/coveragepy>`_.

Byterun is based on pyvm2 written by Paul Swartz (z3p).  




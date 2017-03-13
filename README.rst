Byterun
-------

Byterun is a python interpreter written in just 1451 lines of Python.  If you want to better understand Python, Byterun is  a great place to start.  It has proven very useful to a number of different projects, including one by Google.  

By interpreter we mean a code execution virtual machine.  The Python compiler converts python source code into Python bytecode.  The code execution virtual machine then executes that bytecode.   

There are a number of python virtual machines.  Most Python developers use cPython.  cPython includes a virtual machine written in C.  Yes it runs Python very fast, but it is a large code base, and difficult to understand.  Much better to start by studying Byterun.  Then you can move onto cPython.   

The first step is to read the excellent introductory article on Byterun written by Alison Kaptur.  [A Python Interpreter written in Python](http://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html)

I had to read it a number of times, each time I understood more.  After understanding the article, you should be able to make sense of the code in this repository.  And from there you can move onto studying  cPython, or PyPy, or Jython. 
 
History
-------

[Ned Batchelder](https://nedbatchelder.com/) [started Byterun](https://nedbatchelder.com/blog/201301/byterun_and_making_cells.html) so that he could  get a better understanding of bytecodes so that he could fix branch coverage bugs in 
[coverage.py](https://github.com/nedbat/coveragepy).

Byterun is based on pyvm2 written by Paul Swartz (z3p).  

We invite you to join this community. 




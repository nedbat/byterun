The Python programs whose file names match with test_*.py are used in
testing.

The Python program `compile-file.py` can be used to byte-compile a
program putting it the right `../bytecode-`*x.x* directory.

For example:

```
$ pyenv local 3.3.7
$ python ./compile-file.py test_attributes.py
```

will byte-compile `test_attributes.py` and put the result in
`../bytecode-3.3/test_attributes.pyc`.

The shell program `create-bytecode.sh` will iterate over all python
versions we support and call `compile-file.py` on the given Python
source file. Finally it adds to `git` the bytecode created and
does some administrative cleanup.

To rebuild everything you can thus run:


```
$ ./create-bytecode.sh test_*.py
```

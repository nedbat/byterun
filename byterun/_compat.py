import six

PY3, PY2 = six.PY3, not six.PY3

if six.PY3:
    byteint = lambda b: b
else:
    byteint = ord

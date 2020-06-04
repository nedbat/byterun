# Test LOAD_DEREF among other things
"""This program is self-checking!"""

from functools import wraps
def my_decorator(f):
    dec = wraps(f)
    def wrapper(*args, **kwds):
        # print('Calling decorated function')
        return f(*args, **kwds)
    wrapper = dec(wrapper)
    return wrapper

@my_decorator
def example():
    '''Docstring'''
    return 17

assert example() == 17

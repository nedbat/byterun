def verbose(func):
    def _wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return _wrapper

@verbose
def add(x, y):
    return x+y

add(7, 3)

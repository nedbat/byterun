class GeneratorContextManager(object):
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        try:
            return next(self.gen)
        except StopIteration:
            raise RuntimeError("generator didn't yield")

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                next(self.gen)
            except StopIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                value = type()
            try:
                self.gen.throw(type, value, traceback)
                raise RuntimeError(
                    "generator didn't stop after throw()"
                )
            except StopIteration as exc:
                return exc is not value
            except:
                if sys.exc_info()[1] is not value:
                    raise

def contextmanager(func):
    def helper(*args, **kwds):
        return GeneratorContextManager(func(*args, **kwds))
    return helper

@contextmanager
def my_context_manager(val):
    yield val

with my_context_manager(17) as x:
    assert x == 17

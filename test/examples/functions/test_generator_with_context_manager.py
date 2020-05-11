from contextlib import contextmanager

def inner():
    yield "I'm inner!"

def foo():
    yield from inner()

    @contextmanager
    def cmgr():
        yield "Context Manager!"
    raise StopIteration(cmgr())

def main():
    with (yield from foo()) as x:
        print(x)

def run(fn, *args):
    x = fn(*args)
    while True:
        try:
            print(next(x))
        except StopIteration as e:
            return e.value
run(main)

# Test of 3.5+ GET_YIELD_FROM_ITER

# Code is from https://stackoverflow.com/questions/41136410/python-yield-from-or-return-a-generator
def add(a, b):
    return a + b

def sqrt(a):
    return a ** 0.5

data1 = [*zip(range(1, 3))]  # [(1,), (2,)]

job1 = (sqrt, data1)

def gen_factory(func, seq):
    """Generator factory returning a generator."""
    # do stuff ... immediately when factory gets called
    print("build generator & return")
    return (func(*args) for args in seq)

def gen_generator(func, seq):
    """Generator yielding from sub-generator inside."""
    # do stuff ... first time when 'next' gets called
    print("build generator & yield")
    yield from (func(*args) for args in seq)

gen_fac = gen_factory(*job1)
print(gen_fac)
# build generator & return <-- printed immediately
print(next(gen_fac))  # start
# Out: 1.0
print([*gen_fac])  # deplete rest of generator
# Out: [1.4142135623730951]

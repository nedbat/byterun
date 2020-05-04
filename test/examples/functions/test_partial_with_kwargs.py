from _functools import partial

def f(a,b,c=0,d=0):
    return (a,b,c,d)

f7 = partial(f, b=7, c=1)
them = f7(10)
assert them == (10,7,1,0)

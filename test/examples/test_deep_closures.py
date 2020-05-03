def f1(a):
    b = 2*a
    def f2(c):
        d = 2*c
        def f3(e):
            f = 2*e
            def f4(g):
                h = 2*g
                return a+b+c+d+e+f+g+h
            return f4
        return f3
    return f2
answer = f1(3)(4)(5)(6)
print(answer)
assert answer == 54

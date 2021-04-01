"""This program is self-checking!"""

l = []
for i in range(3):
    try:
        l.append(i)
    finally:
        l.append("f")
    l.append("e")
l.append("r")
print(l)
assert l == [0, "f", "e", 1, "f", "e", 2, "f", "e", "r"]

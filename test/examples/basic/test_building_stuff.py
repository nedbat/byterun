# test code adapted from byterun.py

"""This program is self-checking!"""
two_for_six = (2, 4, 6)
assert (1 + 1, 2 + 2, 3 + 3) == (2, 4, 6)
assert [1 + 1, 2 + 2, 3 + 3] == list(two_for_six)
assert {0: 2, 1: 4, 2: 6} == dict(zip(range(3), two_for_six))

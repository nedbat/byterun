# Test slice expressions
"""This program is self-checking!"""

assert "hello, world"[3:8] == "lo, w"
assert "hello, world"[:8] == "hello, w"
assert "hello, world"[3:] == "lo, world"
assert "hello, world"[:] == "hello, world"
assert "hello, world"[::-1] == "dlrow ,olleh"
assert "hello, world"[3:8:2] == "l,w"

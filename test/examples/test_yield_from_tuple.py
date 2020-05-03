def main():
    for x in outer():
        print(x)

def outer():
    yield from (1, 2, 3, 4)

main()

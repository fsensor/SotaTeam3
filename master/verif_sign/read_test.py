with open("data", 'rb+') as f:
    two = f.read(2)
    three = f.read(3)
    print(two)
    print(three)

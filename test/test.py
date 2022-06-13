import os
from utils import Command

class Test:
    def test1(self, a: int, b: int):
        pass

    def test3(self, a: int, b: int):
        return a * b

    def test2(self, a: int, b: int, d: int):
        return a + b + d

    def test4(self):
        pass


def test1(a):
    return a


def test2():
    return test1(3)


if __name__ == '__main__':
    a = [1, 2]
    b = [1, 2]
    c = {1: 1, 2:2, 3: 3}
    print(4 in c.keys())
    for index, val in enumerate(a):
        print(index, val)
    pass

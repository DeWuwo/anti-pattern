import os
from utils import Command, FileCSV
from collections import defaultdict
from functools import partial

class Test:
    p1: str
    p2: str

    def __init__(self, p1):
        self.p1 = p1
        self.p2 = ''

    def test1(self, a: int, b: int):
        return a + b

    def test3(self, a: int, b: int):
        return a * b

    def test2(self, a: int, b: int, d: int):
        return a + b + d

    def test4(self, p2):
        self.p2 = p2

    def __str__(self):
        return self.p1 + '-' + self.p2


def test1(a):
    return a


def test2():
    return test1(3)


if __name__ == '__main__':
    a = '1.2.3.4'.rsplit('.', 2)
    a[1] = '4'
    print('.'.join(a))
    a = ['Move And Rename Method', 'Move Method', 'Rename Method']
    print("Rename Method" in a)
    print(not 0 ^ 0)
    a = {1: [1, 2], 2: [3, 4]}
    for k, v in a.items():
        print(k, v)
    print(a)
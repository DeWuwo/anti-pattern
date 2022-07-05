import os
from utils import Command, FileCSV


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
    res = FileCSV.read_from_file_csv('C:\\Users\\76723\\Desktop\\test.csv')
    for item in res:
        print(item)

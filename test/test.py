class Test:
    def test1(self, a: int, b: int):
        pass

    def test3(self, a: int, b: int):
        return a * b

    def test2(self, a: int, b: int, d: int):
        return a + b + d

    def test4(self):
        pass


if __name__ == '__main__':
    a = [1, 2]
    b = [1, 2]
    print(a == b)
    pass

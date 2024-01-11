class Compare:
    @classmethod
    def compare_list(cls, left: list, right: list):
        if len(left) != len(right):
            return False
        else:
            inter = set(left) & set(right)
            if len(inter) != len(left):
                return False
        return True


if __name__ == '__main__':
    print(Compare.compare_list([1, 2, 3], [2, 3, 1, 1]))

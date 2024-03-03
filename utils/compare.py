class Compare:
    @classmethod
    def compare_list(cls, left: list, right: list):
        if len(left) != len(right):
            return False
        else:
            if len(left) == 0:
                return True
            else:
                for l, r in zip(left, right):
                    if l != r:
                        return False
                return True


if __name__ == '__main__':
    print(Compare.compare_list([1, 2, 3, 2], [2, 3, 1, 1]))

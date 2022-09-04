from typing import List
from utils import FileJson


class Compare:
    left: str
    right: str

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def get_anti_res(self):
        left: dict = FileJson.read_base_json(self.left)['res']['values']
        right: dict = FileJson.read_base_json(self.right)['res']['values']
        patterns = left.keys()
        return left, right, patterns

    def compare_ref(self):
        left: dict = FileJson.read_base_json(self.left)
        right: dict = FileJson.read_base_json(self.right)
        left_ref = set([int(l) for l in left.keys()])
        right_ref = set([int(r) for r in right.keys()])
        print(len(left_ref), len(right_ref))
        print(left_ref - right_ref)
        print('------------')
        print(right_ref - left_ref)
        print('------------')


def compare(left: dict, right: dict, patterns):
    repeat_count: dict = {}

    def match_example(exa1: List[dict], exa2: List[dict]):
        for rel1, rel2 in zip(exa1, exa2):
            if rel1['src']['category'] != rel2['src']['category'] or \
                    rel1['dest']['category'] != rel2['dest']['category'] or \
                    rel1['src']['qualifiedName'] != rel2['src']['qualifiedName'] or \
                    rel1['dest']['qualifiedName'] != rel2['dest']['qualifiedName'] or \
                    rel1['values'] != rel2['values']:
                return False
        return True

    for pattern in patterns:
        repeat_count[pattern] = {'left': left[pattern]['count'], 'right': right[pattern]['count'], 'repeat': 0}
        old = left[pattern]['examples']
        new = right[pattern]['examples']
        for example1 in old:
            for example2 in new:
                if match_example(example1, example2):
                    repeat_count[pattern]['repeat'] += 1
                    break

    FileJson.write_to_json('D:\\Honor\\test_res', repeat_count, 5)


if __name__ == '__main__':
    cp = Compare('D:\\Honor\\match_res\\LineageOS\\base\\lineage-16.0\\unsure_resolution.json',
                 'D:\\Honor\\match_res\\testos\\base\\lineage-16.0\\unsure_resolution.json')
    cp.compare_ref()

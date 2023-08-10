"""
多版本数据对比脚本，包括
match_rel  依赖的匹配
compare_facade 对比依赖切面
compare_anti 对比反模式
"""
import os
from typing import List
from utils import FileJson, FileCSV


class Compare:

    def __init__(self, out_path, old_version, new_version, left, right):
        """
        共包含五个参数
        out_path     结果输出路径
        old_version  旧版本版本名，用于输出时构造输出文件名
        new_version  新版本版本名，用于输出时构造输出文件名
        left         旧版本<依赖切面， 反模式>结果路径
        right        新版本<依赖切面， 反模式>结果路径
        """
        self.out_path = os.path.join(out_path, f"{old_version}_{new_version}")
        self.left = left
        self.right = right

    def get_anti_res(self):
        left: dict = FileJson.read_base_json(self.left)['res']['values']
        right: dict = FileJson.read_base_json(self.right)['res']['values']
        patterns = left.keys()
        return left, right, patterns

    def get_facade_res(self):
        left: dict = FileJson.read_base_json(self.left)['res']
        right: dict = FileJson.read_base_json(self.right)['res']
        directions = left.keys()
        return left, right, directions

    def compare_facade(self):
        """
        通过读取一个旧版本，一个新版本的依赖界面json结果，生成依赖的数量变化，包括三个维度
        <保留> <新增> <移除>
        同时会生成json文件记录对应 新增 或 移除 的切面详细内容
        """
        left, right, directions = self.get_facade_res()
        compare_count = {}
        compare_res = {}
        compare_res_csv = []
        for dire in directions:
            if dire in ['e2n', 'n2e', 'n2n']:
                compare_count[dire] = {"del": 0, "add": 0, "repeat": 0}
                compare_res[dire] = {"del": [], "add": [], "repeat": []}
            old_facade = left[dire]
            new_facade = right[dire]
            left_match_index = set()
            right_match_index = set()
            for rel1_index in range(0, len(old_facade)):
                for rel2_index in range(0, len(new_facade)):
                    if rel2_index not in right_match_index and Compare.match_rel(old_facade[rel1_index],
                                                                                 new_facade[rel2_index]):
                        left_match_index.add(rel1_index)
                        right_match_index.add(rel2_index)
                        compare_count[dire]['repeat'] += 1
                        # compare_count[dire]['repeat_map'].append([str(rel1_index) + '-' + str(rel2_index)])
                        compare_res[dire]['repeat'].append(new_facade[rel2_index])
                        compare_res_csv.append(dict(**{'facade': dire, 'type': 'repeat'},
                                                    **Compare.rel_to_json(new_facade[rel2_index]))
                                               )
                        break
            del_index = set(range(len(old_facade))) - left_match_index
            add_index = set(range(len(new_facade))) - right_match_index
            for del_exa in del_index:
                compare_count[dire]['del'] += 1
                compare_res[dire]['del'].append(old_facade[del_exa])
                compare_res_csv.append(dict(**{'facade': dire, 'type': 'del'},
                                            **Compare.rel_to_json(old_facade[del_exa]))
                                       )
            for add_exa in add_index:
                compare_count[dire]['add'] += 1
                compare_res[dire]['add'].append(new_facade[add_exa])
                compare_res_csv.append(dict(**{'facade': dire, 'type': 'add'},
                                            **Compare.rel_to_json(new_facade[add_exa]))
                                       )
        FileJson.write_to_json(os.path.join(self.out_path, 'facade_diff'), compare_count, 'count')
        FileJson.write_to_json(os.path.join(self.out_path, 'facade_diff'), compare_res, 'res')
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_diff'), 'res', compare_res_csv, 'w')

    @classmethod
    def match_rel(cls, rel1: dict, rel2: dict):
        if rel1['src']['category'] != rel2['src']['category'] or \
                rel1['dest']['category'] != rel2['dest']['category'] or \
                rel1['src']['qualifiedName'] != rel2['src']['qualifiedName'] or \
                rel1['dest']['qualifiedName'] != rel2['dest']['qualifiedName'] or \
                list(rel1["values"].keys())[0] != list(rel2["values"].keys())[0]:
            return False
        return True

    @classmethod
    def rel_to_json(cls, rel: dict):
        try:
            src_modifier = rel['src']['modifiers']
        except KeyError:
            src_modifier = ''
        try:
            dest_modifier = rel['dest']['modifiers']
        except KeyError:
            dest_modifier = ''
        try:
            src_file = rel['src']['File']
        except KeyError:
            src_file = ''
        try:
            dest_file = rel['dest']['File']
        except KeyError:
            dest_file = ''
        try:
            dest_hidden = rel['dest']['hidden']
        except KeyError:
            dest_hidden = ''
        return {
            "relation": list(rel["values"].keys())[0],
            "src_category": rel["src"]['category'],
            "src_modifier": src_modifier,
            "src_entity": rel['src']['qualifiedName'],
            "src_file": src_file,
            "dest_category": rel['dest']['category'],
            "dest_modifier": dest_modifier,
            "dest_label": dest_hidden,
            "dest_entity": rel['dest']['qualifiedName'],
            "dest_file": dest_file
        }

    def compare_anti(self):
        """
        通过读取一个旧版本，一个新版本的反模式json结果，生成反模式的数量变化，包括三个维度
        <保留> <新增> <移除>
        同时会生成json文件记录对应 新增 或 移除 的切面详细内容
        """
        left, right, patterns = self.get_anti_res()
        repeat_count: dict = {}
        del_exas: dict = {}
        add_exas: dict = {}

        def match_example(exa1: List[dict], exa2: List[dict]):
            for rel1, rel2 in zip(exa1, exa2):
                if not Compare.match_rel(rel1, rel2):
                    return False
            return True

        for pattern in patterns:
            repeat_count[pattern] = {}
            del_exas[pattern] = {'count': 0, 'res': {}}
            add_exas[pattern] = {'count': 0, 'res': {}}
            old = left[pattern]['res']
            new = right[pattern]['res']
            for key, values in old.items():
                old_exa = old[key]['res']
                new_exa = new[key]['res']
                del_exas[pattern]['res'][key] = {'count': 0, 'res': []}
                add_exas[pattern]['res'][key] = {'count': 0, 'res': []}
                repeat_count[pattern][key] = {'left': old[key]['resCount'], 'right': new[key]['resCount'], 'repeat': 0,
                                              'repeat_map': []}
                left_match_index = set()
                right_match_index = set()
                for example1 in range(0, len(old_exa)):
                    for example2 in range(0, len(new_exa)):
                        if example2 not in right_match_index and match_example(old_exa[example1]['values'],
                                                                               new_exa[example2]['values']):
                            left_match_index.add(example1)
                            right_match_index.add(example2)
                            repeat_count[pattern][key]['repeat'] += 1
                            repeat_count[pattern][key]['repeat_map'].append([str(example1) + '-' + str(example2)])
                            break
                del_index = set(range(len(old_exa))) - left_match_index
                add_index = set(range(len(new_exa))) - right_match_index
                for del_exa in del_index:
                    del_exas[pattern]['res'][key]['res'].append(old_exa[del_exa])
                    del_exas[pattern]['res'][key]['count'] += 1
                    del_exas[pattern]['count'] += 1
                for add_exa in add_index:
                    add_exas[pattern]['res'][key]['res'].append(new_exa[add_exa])
                    add_exas[pattern]['res'][key]['count'] += 1
                    add_exas[pattern]['count'] += 1

        FileJson.write_to_json(os.path.join(self.out_path, 'anti_diff'), repeat_count, 'count')
        FileJson.write_to_json(os.path.join(self.out_path, 'anti_diff'), del_exas, 'del_exa')
        FileJson.write_to_json(os.path.join(self.out_path, 'anti_diff'), add_exas, 'add_exa')


if __name__ == '__main__':
    cp = Compare(
        "D:/Honor/match_res/diff/", "lineage18", "lineage19",
        'D:/Honor/match_res/LineageOS/base/lineage-18.1/facade.json',
        'D:/Honor/match_res/LineageOS/base/lineage-19.1/facade.json')
    cp.compare_facade()

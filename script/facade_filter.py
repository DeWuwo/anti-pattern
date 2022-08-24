import os
from typing import List
from collections import defaultdict
from utils import FileCSV, FileJson, Constant


class FacadeFilter:
    file_path: str
    file_name: str
    relation_types: List[str]

    def __init__(self, file_path: str, relation_types: List[str]):
        self.file_path = file_path
        self.file_name = os.path.join(file_path, 'facade.json')
        self.relation_types = relation_types

    def facade_filter(self):
        res = {}
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        for rel_type in self.relation_types:
            res[rel_type + '_e2n'] = 0
            res[rel_type + '_n2e'] = 0
        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                res[rel_type + '_e2n'] += 1
        for rel in n2e:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            if rel_type in self.relation_types:
                if rel_type == Constant.R_annotate:
                    if dest_e['category'] == Constant.E_variable:
                        continue
                res[rel_type + '_n2e'] += 1
        FileCSV.write_dict_to_csv(self.file_path, 'facade_filter', [res], 'w')

    def filter_hidden(self):
        res = defaultdict(int)
        hidden_json = defaultdict(list)
        rel_json = defaultdict(list)
        facade_info = FileJson.read_base_json(self.file_name)
        n2e: List[dict] = facade_info['res']['n2e']
        e2n: List[dict] = facade_info['res']['e2n']
        for rel in e2n:
            src_e = rel['src']
            dest_e = rel['dest']
            rel_type: str = ''
            for k in rel['values'].keys():
                rel_type = str(k)
                break
            try:
                hidden_flag = Constant.hidden_map(dest_e['hidden'])
                if hidden_flag in [Constant.HD_blacklist,
                                   Constant.HD_greylist] + Constant.HD_greylist_max_list:
                    res[hidden_flag] += 1
                    res[rel_type] += 1
                    hidden_json[hidden_flag].append(rel)
                    rel_json[rel_type].append(rel)
            except KeyError:
                pass
        FileCSV.write_dict_to_csv(self.file_path, 'facade_hidden_filter', [res], 'w')
        FileJson.write_data_to_json(self.file_path, hidden_json, 'facade_hidden_hidden.json')
        FileJson.write_data_to_json(self.file_path, rel_json, 'facade_hidden_rel.json')

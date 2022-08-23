import os
from typing import List
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
        n2e: List[dict] = facade_info['res']['0']
        e2n: List[dict] = facade_info['res']['1']
        for rel_type in self.relation_types:
            res[rel_type + '_1'] = 0
            res[rel_type + '_0'] = 0
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
                res[rel_type + '_1'] += 1
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
                res[rel_type + '_0'] += 1
        FileCSV.write_dict_to_csv(self.file_path, 'facade_filter', [res], 'w')

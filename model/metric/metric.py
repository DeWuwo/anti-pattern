import os.path
from typing import List
from collections import defaultdict
from functools import partial

from model.dependency.relation import Relation
from utils import FileCSV


class Metric:
    src_relation: defaultdict
    dest_relation: defaultdict
    mc_data: defaultdict

    def __init__(self, relations: List[Relation], data_path: str):
        src_relation = defaultdict(partial(defaultdict, list))
        dest_relation = defaultdict(partial(defaultdict, list))
        self.mc_data = defaultdict()
        for rel in relations:
            src_relation[rel.src][rel.rel].append(rel)
            dest_relation[rel.dest][rel.rel].append(rel)
        try:
            mc_data_list = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc.csv'))
        except FileNotFoundError:
            mc_data_list = []
        for data in mc_data_list:
            self.mc_data[str(data['filename']).replace('\\', '/')] = data

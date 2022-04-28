import threading
import os
from typing import List, Dict
from collections import defaultdict
from model.relation import Relation
from model.entity import Entity
from model.build_model import BuildModel
from model.pattern_type import PatternType
from utils import FileJson, FileCSV


class Match:
    base_model: BuildModel
    output: str
    match_result: List[Dict[str, List[List[Relation]]]]
    match_result_base_statistic: Dict[str, Dict[str, int]]
    statistic_files: Dict[str, Dict[str, int]]
    statistic_entities: Dict[int, Dict[str, int]]

    def __init__(self, model: BuildModel, output: str):
        self.base_model = model
        self.output = output
        self.match_result = []
        self.match_result_base_statistic = {}
        self.statistic_files = {}
        self.statistic_entities = {}

    # 命令中实体属性解析
    def entity_rule(self, entity_stack: List[Relation], entity: dict):
        entity_category: str = entity['category']
        if entity['id'][0] == 'id':
            pre_edge = entity_stack[entity['id'][1]]
            if entity['id'][2] == 0:
                entity_base = pre_edge.src['id']
            else:
                entity_base = pre_edge.dest['id']
        elif entity['id'][0] == 'bindVar':
            entity_base = entity_stack[entity['id'][1]].bind_var
        else:
            entity_base = entity_category
        entity_attrs: dict = entity['attrs']
        entity_attrs.update({'category': entity_category})
        return entity_base, entity_attrs

    def handle_attr_match(self, entity: Entity, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_{key}', None)
            if not method(entity, val):
                return False
        return True

    def handle_category(self, entity: Entity, category: str):
        return category == '' or entity.category == category

    def handle_accessible(self, entity: Entity, accessible: List[str]):
        return (not accessible) or entity.accessible in accessible or (entity.accessible == '' and '' in accessible)

    def handle_intrusive(self, entity: Entity, intrusive: bool):
        return (not intrusive) or entity.is_intrusive

    def handle_hidden(self, entity: Entity, hidden: bool):
        return (not hidden) or entity.id in self.base_model.hidden_entities

    def handle_final(self, entity: Entity, final: bool):
        return (not final) or entity.id in self.base_model.final_modify_entities

    def handle_accessible_modify(self, entity: Entity, accessible_modify: bool):
        return (not accessible_modify) or entity.id in self.base_model.access_modify_entities

    def handle_hidden_modify(self, entity: Entity, hidden_modify: bool):
        return (not hidden_modify) or entity.id in self.base_model.hidden_modify_entities

    # 匹配函数
    def handle_matching(self, result_set: list, example_stack: list, flag: list, rules: List[dict], current):
        src = rules[current]['src']
        rel = rules[current]['rel']
        dest = rules[current]['dest']
        not_aosp = rules[current]['direction']
        src_base, src_attr = self.entity_rule(example_stack, src)
        dest_base, dest_attr = self.entity_rule(example_stack, dest)
        if len(rules) == 1:
            flag_map = defaultdict(list)
            for item in self.base_model.query_relation(rel, not_aosp, src_base, dest_base):
                if self.handle_attr_match(self.base_model.entity_assi[item.src['id']], **src_attr) and \
                        self.handle_attr_match(self.base_model.entity_assi[item.dest['id']], **dest_attr):
                    flag_map[item.src['id']].append(item)
            for item in flag_map:
                result_set.append(flag_map[item])
        else:
            for item in self.base_model.query_relation(rel, not_aosp, src_base, dest_base):
                if self.handle_attr_match(self.base_model.entity_assi[item.src['id']], **src_attr) and \
                        self.handle_attr_match(self.base_model.entity_assi[item.dest['id']], **dest_attr) and \
                        str(item.src['id']) + str(item.dest['id']) not in flag:
                    next_stack = example_stack[:]
                    next_stack.append(item)
                    flag_update = flag[:]
                    flag_update.append(str(item.src['id']) + str(item.dest['id']))
                    if current < len(rules) - 1:
                        current += 1
                        self.handle_matching(result_set, next_stack, flag_update, rules, current)
                        current -= 1
                    else:
                        result_set.append(next_stack)

    def general_rule_matching(self, pattern: str, rules: list):
        """
        通用的模式匹配
        :return:
        """
        print('      detect Pattern: ', pattern)
        res = []
        for item in rules:
            mode_set = []
            self.handle_matching(mode_set, [], [], item, 0)
            res.extend(mode_set)
        self.match_result.append({pattern: res})

    def pre_del(self):
        self.match_result = []
        self.match_result_base_statistic = {}
        self.statistic_files = {}
        self.statistic_entities = {}

    # 统计
    def get_root_file(self, entity_id: int) -> Entity:
        temp = self.base_model.entity_assi[entity_id]
        while temp.category != 'File':
            temp = self.base_model.entity_assi[temp.parentId]
        return temp

    def get_statistics(self):
        self.match_result_base_statistic['Total'] = {'files_count': self.base_model.statistics_assi['File']}
        for item in self.match_result:
            for pattern in item:
                self.match_result_base_statistic[pattern] = {}
                pattern_files_set = defaultdict(int)
                pattern_entities_set = defaultdict(int)
                for exa in item[pattern]:
                    temp_file_set = set()
                    temp_entity_set = set()
                    for rel in exa:
                        temp_entity_set.add(rel.src['id'])
                        temp_entity_set.add(rel.dest['id'])
                        temp_file_set.add(self.get_root_file(rel.src['id']).file_path)
                        temp_file_set.add(self.get_root_file(rel.dest['id']).file_path)
                    for file_name in temp_file_set:
                        pattern_files_set[file_name] += 1
                    for entity_id in temp_entity_set:
                        pattern_entities_set[entity_id] += 1
                self.match_result_base_statistic[pattern] = {'example_count': len(item[pattern]),
                                                             'entities_count': len(pattern_entities_set),
                                                             'entities': pattern_entities_set,
                                                             'files_count': len(pattern_files_set),
                                                             'files': pattern_files_set}
                for file_name in pattern_files_set:
                    try:
                        self.statistic_files[file_name][pattern] = pattern_files_set[file_name]
                    except KeyError:
                        self.statistic_files[file_name] = {'file_name': file_name}
                        self.statistic_files[file_name][pattern] = pattern_files_set[file_name]
                for entity_id in pattern_entities_set:
                    try:
                        self.statistic_entities[entity_id][pattern] = pattern_entities_set[entity_id]
                    except KeyError:
                        self.statistic_entities[entity_id] = self.base_model.entity_assi[entity_id].to_csv()
                        self.statistic_entities[entity_id][pattern] = pattern_entities_set[entity_id]

    def ready_for_write(self):
        match_set = []
        union_temp: List = []
        re_map = defaultdict(int)
        anti_patterns = {}
        total_count = 0
        anti_patterns['modeCount'] = len(self.match_result)
        anti_patterns['totalCount'] = total_count
        anti_patterns['values'] = {}
        for item in self.match_result:
            for mode in item:
                anti_temp = []
                for exa in item[mode]:
                    anti_temp.append(self.show_details(exa))
                    for rel in exa:
                        s2d = str(rel.src['id']) + str(rel.dest['id'])
                        if re_map[s2d] == 0:
                            re_map[s2d] = 1
                            union_temp.append(self.to_detail_json(rel))
                match_set.append({mode: anti_temp})
                anti_patterns['values'][mode] = {}
                anti_patterns['values'][mode]['count'] = len(anti_temp)
                anti_patterns['values'][mode]['examples'] = anti_temp
                total_count += len(anti_temp)
        anti_patterns['totalCount'] = total_count
        return match_set, union_temp, anti_patterns

    def to_detail_json(self, relation: Relation):
        return {"src": self.base_model.entity_assi[relation.src['id']].toJson(), "values": {relation.rel: 1},
                "dest": self.base_model.entity_assi[relation.dest['id']].toJson()}

    def show_details(self, section: List[Relation]):
        temp = []
        for index, item in enumerate(section):
            temp.append(self.to_detail_json(item))
        return temp

    def start_match_pattern(self, pattern: PatternType):
        print('start detect ', pattern.ident)
        threads = []
        self.pre_del()
        for rule in pattern.rules:
            for key, val in rule.items():
                th = threading.Thread(target=self.general_rule_matching(key, val))
                threads.append(th)
        for th in threads:
            th.setDaemon(False)
            th.start()
        for th in threads:
            th.join()
        self.get_statistics()
        match_set, match_set_union, match_set_json_res = self.ready_for_write()
        self.output_res(pattern.ident, match_set, match_set_union, match_set_json_res)
        self.output_statistic(pattern.ident, pattern.patterns, self.match_result_base_statistic,
                              self.statistic_files, self.statistic_entities)

    def output_res(self, pattern_type: str, match_set, match_set_union, match_set_json_res):
        output_path = os.path.join(self.output, pattern_type)
        FileJson.write_match_mode(output_path, match_set)
        FileJson.write_to_json(output_path, match_set_union, 1)
        FileJson.write_to_json(output_path, match_set_json_res, 3)

    def output_statistic(self, pattern_type: str, patterns: List[str], match_result_base_statistic,
                         statistic_files_pattern, statistic_entities_pattern):
        output_path = os.path.join(self.output, pattern_type)
        FileJson.write_to_json(output_path, match_result_base_statistic, 4)
        # FileCSV.write_stat_to_csv(coupling_path, date.today(), args.honor, args.android, match_set_stat)
        headers = ['file_name']
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'file-pattern', headers, statistic_files_pattern)
        headers = Entity.get_csv_header()
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'entity-pattern', headers, statistic_entities_pattern)

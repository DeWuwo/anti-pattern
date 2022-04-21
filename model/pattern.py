import threading
from typing import List
from collections import defaultdict
from model.match import Match
from model.entity import Entity
from model.relation import Relation


class Pattern:
    match: Match

    def __init__(self, match: Match):
        self.match = match

    def matchPattern(self, patterns: list):
        threads = []
        self.match.pre_del()
        for pattern in patterns:
            for key, val in pattern.items():
                th = threading.Thread(target=self.match.general_rule_matching(key, val))
                threads.append(th)
        for th in threads:
            th.setDaemon(False)
            th.start()
        for th in threads:
            th.join()
        match_set_stat = self.get_statistics()
        match_set, union_temp, anti_patterns = self.ready_for_write()
        return match_set_stat, match_set, union_temp, anti_patterns

    def get_statistics(self):
        def get_root_file(entity_id: int) -> Entity:
            temp = self.match.base_model.entity_assi[entity_id]
            while temp.category != 'File':
                temp = self.match.base_model.entity_assi[temp.parentId]
            return temp

        self.match.match_result_statistic['Total'] = {'files_count': self.match.base_model.statistics_assi['File']}
        for item in self.match.match_result:
            for mode in item:
                self.match.match_result_statistic[mode] = {}
                files_set = defaultdict(int)
                entities_set = defaultdict(int)
                for exa in item[mode]:
                    temp_file_set = set()
                    temp_entity_set = set()
                    for rel in exa:
                        temp_entity_set.add(rel.src['id'])
                        temp_entity_set.add(rel.dest['id'])
                        temp_file_set.add(get_root_file(rel.src['id']).qualifiedName)
                        temp_file_set.add(get_root_file(rel.dest['id']).qualifiedName)
                    for file_name in temp_file_set:
                        files_set[file_name] += 1
                    for entity_id in temp_entity_set:
                        entities_set[entity_id] += 1
                self.match.match_result_statistic[mode] = {'example_count': len(item[mode]),
                                                           'entities_count': len(entities_set),
                                                           'entities': entities_set,
                                                           'files_count': len(files_set),
                                                           'files': files_set}
        return self.match.match_result_statistic

    def ready_for_write(self):
        match_set = []
        union_temp: List = []
        re_map = defaultdict(int)
        anti_patterns = {}
        total_count = 0
        anti_patterns['modeCount'] = len(self.match.match_result)
        anti_patterns['totalCount'] = total_count
        anti_patterns['values'] = {}
        for item in self.match.match_result:
            for mode in item:
                anti_temp = []
                for exa in item[mode]:
                    anti_temp.append(self.show_details(exa))
                    for rel in exa:
                        s2d = str(rel.src['id']) + str(rel.dest['id'])
                        if re_map[s2d] == 0:
                            re_map[s2d] = 1
                            union_temp.append(self.toDetailJson(rel))
                match_set.append({mode: anti_temp})
                anti_patterns['values'][mode] = {}
                anti_patterns['values'][mode]['count'] = len(anti_temp)
                anti_patterns['values'][mode]['examples'] = anti_temp
                total_count += len(anti_temp)
        anti_patterns['totalCount'] = total_count
        return match_set, union_temp, anti_patterns

    def toDetailJson(self, relation: Relation):
        return {"src": self.match.base_model.entity_assi[relation.src['id']].toJson(), "values": {relation.rel: 1},
                "dest": self.match.base_model.entity_assi[relation.dest['id']].toJson()}

    def show_details(self, section: List[Relation]):
        temp = []
        for index, item in enumerate(section):
            temp.append(self.toDetailJson(item))
        return temp

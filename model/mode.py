import threading
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.relation import Relation
from model.entity import Entity
from utils.constant import Constant
from model.build_model import BuildModel


class ModeMatch:
    entity_stat_honor: Dict
    # base model
    base_model: BuildModel
    # find set
    find_map: defaultdict
    # out set
    match_set: List[Dict[str, List[List[Relation]]]]
    match_set_stat: Dict[str, Dict[str, int]]
    anti_patterns: List[Dict[str, List[list]]]

    def __init__(self, base_model: BuildModel, entity_stat_honor, android_contain_set):
        self.entity_stat_honor = entity_stat_honor
        self.find_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        self.match_set = []
        self.match_set_stat = {}
        self._init(base_model.diff_relations, android_contain_set)

    def _init(self, section: List[Relation], android_contain_set: List[Relation]):
        for item in section:
            self.find_map[item.rel][str(item.src['not_aosp']) + str(item.dest['not_aosp'])][
                self.base_model.entity_assi[item.src['id']].category][
                self.base_model.entity_assi[item.dest['id']].category].append(item)

            self.find_map[item.rel][str(item.src['not_aosp']) + str(item.dest['not_aosp'])][
                self.base_model.entity_assi[item.src['id']].category][item.dest['id']].append(item)

            self.find_map[item.rel][str(item.src['not_aosp']) + str(item.dest['not_aosp'])][item.src['id']][
                self.base_model.entity_assi[item.dest['id']].category].append(item)

            self.find_map[item.rel][str(item.src['not_aosp']) + str(item.dest['not_aosp'])][item.src['id']][
                item.dest['id']].append(item)
            if item.bind_var != -1:
                self.find_map[item.bind_var][str(item.src['not_aosp']) + str(item.dest['not_aosp'])][
                    self.base_model.entity_assi[item.src['id']].category][
                    self.base_model.entity_assi[item.dest['id']].category].append(item)
        for item in android_contain_set:
            self.find_map[item.rel]['00'][item.src['id']][item.dest['id']].append(item)

    def findSection(self, rel: str, not_aosp: str, src, dest) -> List[Relation]:
        return self.find_map[rel][not_aosp][src][dest]

    def findModeICCD1(self):
        print("matching mode <Inheritance class coupling dependency (1)>")
        mode_set = []
        for item in self.findSection(Constant.inherit, '01', Constant.E_class, Constant.E_class):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/InheritClassCouplingDep': mode_set})
        mode_set = []
        for item in self.findSection(Constant.implement, '01', Constant.E_class, Constant.E_interface):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/ImplementClassCouplingDep': mode_set})

    def findModeIUP(self):
        print("matching mode <Inheritance Use Parent Protected Dep>")
        mode_set = []
        for item in self.findSection(Constant.inherit, '10', Constant.E_class, Constant.E_class):
            temp = [item]
            for item2 in self.findSection(Constant.define, '11', item.src['id'], Constant.E_method):
                flag = 1
                temp.append(item2)
                for item3 in self.findSection(Constant.call, '10', item2.dest['id'], Constant.E_method) + \
                             self.findSection(Constant.use, '10', item2.dest['id'], Constant.E_variable):
                    if 'protected' in self.base_model.entity_assi[item3.dest['id']].modifiers:
                        if item3.bind_var != -1:
                            item4 = self.findSection(Constant.define, '00', item.dest['id'], item3.bind_var)
                        else:
                            item4 = self.findSection(Constant.define, '00', item.dest['id'], item3.dest['id'])
                        if len(item4):
                            temp.append(item4[0])
                            temp.append(item3)
                            flag = 2
                if flag == 1:
                    temp.pop()
                elif flag == 2:
                    mode_set.append(temp)
        self.match_set.append({'Honor2Android/InheritanceUseParentProtected': mode_set})

    def findModeRUD(self):
        print("matching mode 2......")
        mode_set = []
        for item in self.findSection('Reflect', '10', -1, -1):
            if item.rel == 'Reflect':
                temp = [item, self.base_model.entity_assi[self.base_model.entity_assi[item.src['id']].parentId]]
                flag = 0
                for item2 in self.findSection('Reflect', '10', -1, -1):
                    flag = 0
                    if item.dest['id'] == item2.src['id'] and item2.rel == 'Contain' and \
                            self.base_model.entity_assi[item2.dest['id']].category == 'Method':
                        flag = 1
                        temp.append(item2)
                        for item3 in self.findSection('Call', '10', -1, -1):
                            if item3.rel == 'Call' and item3.src['id'] == item2.dest['id'] and \
                                    item3.dest['id'] == item.src['id']:
                                flag = 2
                                temp.append(item3)
                if flag == 2:
                    mode_set.append(temp)
                elif flag == 1:
                    temp.pop()

        self.match_set.append({'mode2': mode_set})

    def findModeAOSPUA(self):
        print("matching mode <AOSP Use Aggregation extension class Dependency>")
        # mode3_set = []
        mode4_set = []
        for item in self.findSection(Constant.define, '01', Constant.E_class, Constant.E_variable):
            temp = [item]
            for item1 in self.findSection(Constant.implement, '11', Constant.E_class, Constant.E_interface):
                if self.base_model.entity_assi[item1.dest['id']].name == \
                        self.base_model.entity_assi[item.dest['id']].raw_type:
                    temp1 = temp[:]
                    temp1.append(item1)
                    for item2 in self.findSection(Constant.define, '11', item1.src['id'], Constant.E_method):
                        flag = 1
                        # temp33 = temp1[:]
                        # temp33.append(item2)
                        temp44 = temp1[:]
                        temp44.append(item2)
                        # for item3 in self.findSection('Call', '10', item2.dest['id'], 'Method'):
                        #     item4 = self.findSection('Define', '00', item.src['id'], item3.dest['id'])
                        #     if len(item4) == 1:
                        #         temp33.append(item4[0])
                        #         temp33.append(item3)
                        #         flag = 2
                        # if flag == 2:
                        #     mode3_set.append(temp33)
                        #     flag = 1
                        for item3 in self.findSection(Constant.call, '01', Constant.E_method, item2.dest['id']):
                            if item3.bind_var == item.dest['id']:
                                item4 = self.findSection(Constant.define, '00', item.src['id'], item3.src['id'])
                                if item4:
                                    temp44.append(item4[0])
                                    temp44.append(item3)
                                    flag = 2
                        if flag == 2:
                            mode4_set.append(temp44)
        # self.match_set.append({'Honor2Android/AggregationExtensionClassDep': mode3_set})
        self.match_set.append({'Android2Honor/AggregationExtensionClassDep': mode4_set})

    def findModeAUAOSP(self):
        print("matching mode <Aggregation Use AOSP Dependency>")
        mode_set = []
        for item in self.findSection(Constant.define, '11', Constant.E_class, Constant.E_variable):
            temp = [item]
            for item1 in self.findSection(Constant.define, '11', item.src['id'], Constant.E_method):
                flag = 1
                temp1 = temp[:]
                temp1.append(item1)
                for item2 in self.findSection(Constant.call, '10', item1.dest['id'], Constant.E_method):
                    if item2.bind_var == item.dest['id']:
                        item3 = self.findSection(Constant.define, '00',
                                                 self.base_model.entity_assi[item2.bind_var].raw_type,
                                                 item2.dest['id'])
                        if item3:
                            flag = 2
                            temp1.append(item3[0])
                            temp1.append(item2)
                if flag == 2:
                    mode_set.append(temp1)

        self.match_set.append({'Honor2Android/AggregationUseAOSpDep': mode_set})

    def findModeIECUS(self):
        print("matching mode <Inner Extension class use dependency>")
        mode_set = []
        for item in self.findSection(Constant.define, '01', Constant.E_class, Constant.E_class):
            temp = [item]
            for item2 in self.findSection(Constant.define, '11', item.dest['id'], Constant.E_method):
                flag = 1
                temp.append(item2)
                for item3 in self.findSection(Constant.call, '10', item2.dest['id'], Constant.E_method):
                    item4 = self.findSection(Constant.define, '00', item.src['id'], item3.dest['id'])
                    if item4:
                        temp.append(item4[0])
                        temp.append(item3)
                        flag = 2
                if flag == 1:
                    temp.pop()
                elif flag == 2:
                    mode_set.append(temp)

        self.match_set.append({'Honor2Android/InnerExtensionClassUseDep': mode_set})

    def findModeEAED(self):
        print("matching mode Encapsulation of AOSP exposes dep")
        mode_set = []
        for item in self.findSection(Constant.define, '11', Constant.E_class, Constant.E_variable):
            temp = [item]
            for item2 in self.findSection(Constant.define, '00', self.base_model.entity_assi[item.dest['id']].raw_type,
                                          Constant.E_method):
                if self.base_model.entity_assi[item2.src['id']].category == 'Interface':
                    flag = 1
                    temp.append(item2)
                    for item3 in self.findSection(Constant.define, '11', item.src['id'], Constant.E_method):
                        item4 = self.findSection(Constant.call, '10', item3.dest['id'], item2.dest['id'])
                        if item4:
                            temp.append(item4[0])
                            temp.append(item3)
                            flag = 2
                    if flag == 1:
                        temp.pop()
                    elif flag == 2:
                        mode_set.append(temp)
        self.match_set.append({'mode7': mode_set})

    def findModePLCD(self):
        print("matching mode <Parameter list change dependency>")
        mode_set = []
        for item in self.findSection(Constant.param, '01', Constant.E_method, Constant.E_variable):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/ParameterListModifyDep': mode_set})

    def findModePIUD(self):
        print("matching mode <Public Interface Use Dependency>")
        mode_set = []
        for item in self.findSection(Constant.call, '10', Constant.E_method, Constant.E_method):
            if 'private' not in self.base_model.entity_assi[item.dest['id']].modifiers and \
                    'protected' not in self.base_model.entity_assi[item.dest['id']].modifiers:
                mode_set.append([item])
        self.match_set.append({'Honor2Android/PublicInterfaceUseDep': mode_set})

    def general_rule_matching(self, rules):
        """
        通用的模式匹配
        :return:
        """
        rules = [
            [{'id': [-1], 'category': 'Class', 'accessible': []}, 'Inherit',
             {'id': [-1], 'category': 'Class', 'accessible': []}, '10'],
            [{'id': ['id', 0, 0], 'category': 'Class', 'accessible': []}, 'Define',
             {'id': [-1], 'category': 'Method', 'accessible': []}, '11'],
            [{'id': ['id', 1, 1], 'category': 'Method', 'accessible': []}, 'Call',
             {'id': [-1], 'category': 'Method', 'accessible': ['protected']}, '10'],
            [{'id': ['id', 0, 1], 'category': 'Class', 'accessible': []}, 'Define',
             {'id': ['bindType', 2], 'category': 'Variable', 'accessible': ['protected']}, '00']
        ]

        # 命令中实体属性解析
        def entity_rule(entity_stack: List[Relation], entity: dict):
            entity_accessible = entity['accessible']
            entity_category = entity['category']
            if entity['id'][0] == 'id':
                pre_edge = entity_stack[entity['id'][1]]
                if entity['id'][2] == 0:
                    entity_base = pre_edge.src['id']
                else:
                    entity_base = pre_edge.dest['id']
            elif entity['id'][0] == 'type':
                pre_edge = entity_stack[entity['id'][1]]
                if entity['id'][2] == 0:
                    entity_base = self.base_model.entity_assi[pre_edge.src['id']].raw_type
                else:
                    entity_base = self.base_model.entity_assi[pre_edge.dest['id']].raw_type
            elif entity['id'][0] == 'bindType':
                entity_base = entity_stack[entity['id'][1]].bind_var
            else:
                entity_base = entity_category
            return entity_base, entity_category, entity_accessible

        # 匹配函数
        def handle_matching(result_set: list, example_stack: list, flag: list, graph, current):
            src = graph[current][0]
            rel = graph[current][1]
            dest = graph[current][2]
            not_aosp = graph[current][3]
            src_base, src_category, src_access = entity_rule(example_stack, src)
            dest_base, dest_category, dest_access = entity_rule(example_stack, dest)
            for item in self.findSection(rel, not_aosp, src_base, dest_base):
                if (src_category == '' or src_category == self.base_model.entity_assi[item.src['id']].category) and \
                        (dest_category == '' or dest_category == self.base_model.entity_assi[
                            item.dest['id']].category) and \
                        (not src_access or self.base_model.entity_assi[item.src['id']].accessible in src_access) and \
                        (not dest_access or self.base_model.entity_assi[item.dest['id']].accessible in dest_access) and \
                        str(item.src['id']) + str(item.dest['id']) not in flag:
                    next_stack = example_stack[:]
                    next_stack.append(item)
                    flag_update = flag[:]
                    flag_update.append(str(item.src['id']) + str(item.dest['id']))
                    if current < len(graph) - 1:
                        current += 1
                        handle_matching(result_set, next_stack, flag_update, graph, current)
                        current -= 1
                    else:
                        result_set.append(next_stack)

        mode_set = []
        handle_matching(mode_set, [], [], rules, 0)
        self.match_set.append({'users/tt2': mode_set})

    def matchMode(self):
        threads = []
        t1 = threading.Thread(target=self.findModeICCD1())
        threads.append(t1)
        t12 = threading.Thread(target=self.findModeIUP())
        threads.append(t12)
        t3 = threading.Thread(target=self.findModeAUAOSP())
        threads.append(t3)
        t34 = threading.Thread(target=self.findModeAOSPUA())
        threads.append(t34)
        t6 = threading.Thread(target=self.findModeIECUS())
        threads.append(t6)
        # t7 = threading.Thread(target=self.findMode7())
        # threads.append(t7)
        t8 = threading.Thread(target=self.findModePLCD())
        threads.append(t8)
        t9 = threading.Thread(target=self.findModePIUD())
        threads.append(t9)
        # a1 = threading.Thread(target=self.findACM())
        # threads.append(a1)

        for th in threads:
            th.setDaemon(False)
            th.start()
        for th in threads:
            th.join()
        match_set_stat = self.get_statistics()
        match_set, union_temp, anti_patterns = self.ready_for_write()
        return match_set_stat, match_set, union_temp, anti_patterns

    def get_statistics(self):
        def get_root_file(entityId: int) -> Entity:
            temp = self.base_model.entity_assi[entityId]
            while temp.category != 'File':
                temp = self.base_model.entity_assi[temp.parentId]
            return temp

        self.match_set_stat['Total'] = {'files_count': self.entity_stat_honor['File']}
        for item in self.match_set:
            for mode in item:
                self.match_set_stat[mode] = {}
                files_set = defaultdict(int)
                for exa in item[mode]:
                    temp_set = set()
                    for rel in exa:
                        temp_set.add(get_root_file(rel.src['id']).qualifiedName)
                        temp_set.add(get_root_file(rel.dest['id']).qualifiedName)
                    for file_name in temp_set:
                        files_set[file_name] += 1
                self.match_set_stat[mode] = {'example_count': len(item[mode]), 'files_count': len(files_set),
                                             'files': files_set}
        return self.match_set_stat

    def ready_for_write(self):
        match_set = []
        union_temp: List = []
        re_map = defaultdict(int)
        anti_patterns = {}
        total_count = 0
        anti_patterns['modeCount'] = len(self.match_set)
        anti_patterns['totalCount'] = total_count
        anti_patterns['values'] = {}
        for item in self.match_set:
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
        return {"src": self.base_model.entity_assi[relation.src['id']].toJson(), "values": {relation.rel: 1},
                "dest": self.base_model.entity_assi[relation.dest['id']].toJson()}

    def show_details(self, section: List[Relation]):
        temp = []
        for index, item in enumerate(section):
            temp.append(self.toDetailJson(item))
        return temp

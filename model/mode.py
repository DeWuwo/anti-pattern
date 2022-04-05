import threading
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.relation import Relation
from model.entity import Entity
from utils.constant import Constant


class ModeMatch:
    honors: List[Entity]
    entity_stat_honor: Dict
    # find set
    find_map: defaultdict
    android_contain_map: defaultdict
    # out set
    match_set: List[Dict[str, List[List[Relation]]]]
    match_set_stat: Dict[str, Dict[str, int]]
    anti_patterns: List[Dict[str, List[list]]]

    def __init__(self, honors, entity_stat_honor, diff, android_contain_set):
        self.honors = honors
        self.entity_stat_honor = entity_stat_honor
        self.find_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        self.match_set = []
        self.match_set_stat = {}
        self._init(diff, android_contain_set)

    def _init(self, section: List[Relation], android_contain_set: List[Relation]):
        for item in section:
            self.find_map[item.rel][str(item.src['isHonor']) + str(item.dest['isHonor'])][
                self.honors[item.src['id']].category][self.honors[item.dest['id']].category].append(item)

            self.find_map[item.rel][str(item.src['isHonor']) + str(item.dest['isHonor'])][
                self.honors[item.src['id']].category][item.dest['id']].append(item)

            self.find_map[item.rel][str(item.src['isHonor']) + str(item.dest['isHonor'])][item.src['id']][
                self.honors[item.dest['id']].category].append(item)

            self.find_map[item.rel][str(item.src['isHonor']) + str(item.dest['isHonor'])][item.src['id']][
                item.dest['id']].append(item)
        for item in android_contain_set:
            self.find_map[item.rel]['00'][item.src['id']][item.dest['id']].append(item)

    def findSection(self, rel: str, isHonor: str, src, dest) -> List[Relation]:
        return self.find_map[rel][isHonor][src][dest]

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
                    if 'protected' in self.honors[item3.dest['id']].modifiers:
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
                temp = [item, self.honors[self.honors[item.src['id']].parentId]]
                flag = 0
                for item2 in self.findSection('Reflect', '10', -1, -1):
                    flag = 0
                    if item.dest['id'] == item2.src['id'] and item2.rel == 'Contain' and \
                            self.honors[item2.dest['id']].category == 'Method':
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
                if self.honors[item1.dest['id']].name == self.honors[item.dest['id']].var_type:
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
                        item3 = self.findSection(Constant.define, '00', self.honors[item2.bind_var].var_type,
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
            for item2 in self.findSection(Constant.define, '00', self.honors[item.dest['id']].var_type,
                                          Constant.E_method):
                if self.honors[item2.src['id']].category == 'Interface':
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
        self.match_set.append({'Android2Honor/ParameterListChangeDep': mode_set})

    def findModePIUD(self):
        print("matching mode <Public Interface Use Dependency>")
        mode_set = []
        for item in self.findSection(Constant.call, '10', Constant.E_method, Constant.E_method):
            if 'private' not in self.honors[item.dest['id']].modifiers and \
                    'protected' not in self.honors[item.dest['id']].modifiers:
                mode_set.append([item])
        self.match_set.append({'Honor2Android/PublicInterfaceUseDep': mode_set})

    def test_find(self):
        """
        通用的模式匹配
        :return:
        """
        tt = [[[-1, 'Class'], 'Contain', [-1, 'Class'], '01'], [[0, 1], 'Contain', [-1, 'Method'], '11'],
              [[1, 1], 'Call', [-1, 'Method'], '10'], [[0, 0], 'Contain', [2, 1], '00']]
        tt1 = [[{'id': [-1], 'category': 'Class', 'type': [-1], 'access': ''}, 'Contain',
                {'id': [-1], 'category': 'Class', 'type': [-1], 'access': ''}, '01'],
               [{'id': [0, 1], 'category': '', 'type': [-1], 'access': ''}, 'Contain',
                {'id': [-1], 'category': 'Method', 'type': [-1], 'access': ''}, '11'],
               [{'id': [1, 1], 'category': '', 'type': [-1], 'access': ''}, 'Call',
                {'id': [-1], 'category': 'Method', 'type': [-1], 'access': ''}, '10'],
               [{'id': [0, 0], 'category': '', 'type': [-1], 'access': ''}, 'Contain',
                {'id': [2, 1], 'category': '', 'type': [-1], 'access': ''}, '00']]
        tt2 = [[{'id': [-1], 'category': 'Class', 'type': [-1], 'access': ''}, 'Implement',
                {'id': [-1], 'category': 'Interface', 'type': [-1], 'access': ''}, '01']]

        # 命令中实体属性解析
        def entity_rule(entity_stack: list, entity: dict):
            entity_access = entity['access']

            if entity['id'][0] != -1:
                entity_base = entity_stack[entity['id'][0]].dest['id'] if entity['id'][1] == 1 else \
                    entity_stack[entity['id'][0]].src['id']
            elif entity['type'][0] != -1:
                entity_base = entity_stack[entity['type'][0]].dest['id'] if entity['type'][1] == 1 else \
                    entity_stack[entity['type'][0]].src['id']
            else:
                entity_base = entity['category']
            return entity_base, entity_access

        # 匹配函数
        def my_find(result_set: list, example_stack: list, graph, current):
            src = graph[current][0]
            rel = graph[current][1]
            dest = graph[current][2]
            isHonor = graph[current][3]
            src_base, src_access = entity_rule(example_stack, src)
            dest_base, dest_access = entity_rule(example_stack, dest)
            for item in self.findSection(rel, isHonor, src_base, dest_base):
                if (src_access == '' or src_access in self.honors[item.src['id']].modifiers) and (
                        dest_access == '' or dest_access in self.honors[item.dest['id']].modifiers):
                    next_stack = example_stack[:]
                    next_stack.append(item)
                    if current < len(graph) - 1:
                        current += 1
                        my_find(result_set, next_stack, graph, current)
                        current -= 1
                    else:
                        result_set.append(next_stack)

        mode_set = []
        my_find(mode_set, [], tt1, 0)
        self.match_set.append({'users/tt1': mode_set})
        mode_set = []
        my_find(mode_set, [], tt2, 0)
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
        test = threading.Thread(target=self.test_find())
        threads.append(test)

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
            temp = self.honors[entityId]
            while temp.category != 'File':
                temp = self.honors[temp.parentId]
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
        return {"src": self.honors[relation.src['id']].toJson(), "values": {relation.rel: 1},
                "dest": self.honors[relation.dest['id']].toJson()}

    def show_details(self, section: List[Relation]):
        temp = []
        for index, item in enumerate(section):
            temp.append(self.toDetailJson(item))
        return temp

    def findACM(self):
        print('find acm')
        acm_set = []
        for item in self.honors:
            if item.access_change != '' and item.access_change[0] != \
                    item.access_change[1]:
                acm_set.append(item)

import threading
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.relation import Relation
from model.entity import Entity


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

    def findSection(self, rel: str, isHonor: str, src, dest) -> list:
        return self.find_map[rel][isHonor][src][dest]

    def findModeICCD1(self):
        print("matching mode <Inheritance class coupling dependency (1)>")
        mode_set = []
        for item in self.findSection('Inherit', '01', 'Class', 'Class'):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/InheritClassCouplingDep': mode_set})
        mode_set = []
        for item in self.findSection('Implement', '01', 'Class', 'Interface'):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/ImplementClassCouplingDep': mode_set})

    def findModeIUP(self):
        print("matching mode <Inheritance class coupling dependency (2)>")
        mode_set = []
        for item in self.findSection('Inherit', '10', 'Class', 'Class'):
            temp = [item]
            for item2 in self.findSection('Contain', '11', item.src['id'], 'Method'):
                flag = 1
                temp.append(item2)
                for item3 in self.findSection('Call', '10', item2.dest['id'], 'Method') + \
                             self.findSection('Use', '10', item2.dest['id'], 'Variable'):
                    if self.honors[item3.dest['id']].accessibility != 'Public':
                        pid = self.honors[item3.dest['id']].parentId
                        if pid == item.dest['id']:
                            temp.append(item3)
                            temp.append(Relation({'id': item.dest['id'], 'isHonor': 0}, 'Contain',
                                                 {'id': item3.dest['id'], 'isHonor': 0}))
                            flag = 2
                        elif self.honors[pid].name in [self.honors[i.dest['id']].var_type for i in
                                                       self.findSection('Use', '10', item2.dest['id'], 'Variable')]:
                            temp.append(item3)
                            flag = 2
                if flag == 1:
                    temp.pop()
                elif flag == 2:
                    mode_set.append(temp)
        self.match_set.append({'Honor2Android/InheritanceUseParentProtected': mode_set})

    def findMode2(self):
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
        mode3_set = []
        mode4_set = []
        for item in self.findSection('Contain', '01', 'Class', 'Variable'):
            temp = [item]
            for item1 in self.findSection('Implement', '11', 'Class', 'Interface'):
                if self.honors[item1.dest['id']].name == self.honors[item.dest['id']].var_type:
                    temp1 = temp[:]
                    temp1.append(item1)
                    for item2 in self.findSection('Contain', '11', item1.src['id'], 'Method'):
                        flag = 1
                        temp33 = temp1[:]
                        temp33.append(item2)
                        temp44 = temp1[:]
                        temp44.append(item2)
                        for item3 in self.findSection('Call', '10', item2.dest['id'], 'Method'):
                            item4 = self.findSection('Contain', '00', item.src['id'], item3.dest['id'])
                            if len(item4) == 1:
                                temp33.append(item4[0])
                                temp33.append(item3)
                                flag = 2
                        if flag == 2:
                            mode3_set.append(temp33)
                            flag = 1
                        for item3 in self.findSection('Call', '01', 'Method', item2.dest['id']):
                            item4 = self.findSection('Contain', '00', item.src['id'], item3.src['id'])
                            if len(item4) == 1:
                                temp44.append(item4[0])
                                temp44.append(item3)
                                flag = 2
                        if flag == 2:
                            mode4_set.append(temp44)
        self.match_set.append({'Honor2Android/AggregationExtensionClassDep': mode3_set})
        self.match_set.append({'Android2Honor/AggregationExtensionClassDep': mode4_set})

    def findModeAUAOSP(self):
        print("matching mode <Aggregation Use AOSP Dependency>")
        mode_set = []
        for item in self.findSection('Contain', '10', 'Class', 'Variable'):
            temp = [item]
            for item1 in self.findSection('Contain', '11', item.src['id'], 'Method'):
                flag = 1
                temp1 = temp[:]
                temp1.append(item1)
                for item2 in self.findSection('Call', '10', item1.dest['id'], 'Method'):
                    par_entity = self.honors[item2.dest[id]].parentId
                    if self.honors[par_entity].name == self.honors[item.dest['id']].var_type:
                        flag = 2
                        temp1.append(Relation({'id': par_entity, 'isHonor': 0}, 'Contain',
                                              {'id': item2.dest['id'], 'isHonor': 0}))
                        temp1.append(item2)
                if flag == 2:
                    mode_set.append(temp1)

        self.match_set.append({'Honor2Android/AggregationUseAOSpDep': mode_set})

    def findMode5(self):
        pass

    def findModeIECUS(self):
        print("matching mode <Extension class use dependency>")
        mode_set = []
        for item in self.findSection('Contain', '01', 'Class', 'Class'):
            if item.src['id'] == self.honors[item.dest['id']].parentId:
                temp = [item]
                for item2 in self.findSection('Contain', '11', item.dest['id'], 'Method'):
                    flag = 1
                    temp.append(item2)
                    for item3 in self.findSection('Call', '10', item2.dest['id'], 'Method'):
                        if self.honors[item3.dest['id']].parentId == item.src['id']:
                            temp.append(Relation({'id': item.src['id'], 'isHonor': 0}, 'Contain',
                                                 {'id': item3.dest['id'], 'isHonor': 0}))
                            temp.append(item3)
                            flag = 2
                    if flag == 1:
                        temp.pop()
                    elif flag == 2:
                        mode_set.append(temp)

        self.match_set.append({'Honor2Android/InnerExtensionClassUseDep': mode_set})

    def findMode7(self):
        print("matching mode7......")
        mode_set = []
        for item in self.findSection('Contain', '10', -1, -1):
            if self.honors[item.src['id']].category == 'Class' and self.honors[item.dest['id']].category == 'Variable':
                temp = [item]
                for item2 in self.findSection('Contain', '11', -1, -1):
                    if self.honors[item2.src['id']].name == self.honors[item.dest['id']].var_type and \
                            item2.src['id'] == item.src['id'] and self.honors[item2.dest['id']].category == 'Method':
                        flag = 1
                        temp.append(item2)
                        for item3 in self.findSection('Call', '10', -1, -1):
                            if item3.src['id'] == item2.dest['id'] and \
                                    self.honors[item3.dest['id']].parentId == item.dest['id']:
                                temp.append(item3)
                                temp.append(Relation({'id': item.dest['id'], 'isHonor': 0}, 'Contain',
                                                     {'id': item3.dest['id'], 'isHonor': 0}))
                                flag = 2
                        if flag == 1:
                            temp.pop()
                        elif flag == 2:
                            mode_set.append(temp)
        self.match_set.append({'mode7': mode_set})

    def findModePLCD(self):
        print("matching mode <Parameter list change dependency>")
        mode_set = []
        for item in self.findSection('Parameter', '01', 'Method', 'Variable'):
            mode_set.append([item])
        self.match_set.append({'Android2Honor/ParameterListChangeDep': mode_set})

    def findModePIUD(self):
        print("matching mode <Public Interface Use Dependency>")
        mode_set = []
        for item in self.findSection('Call', '10', 'Method', 'Method'):
            if self.honors[item.dest['id']].accessibility == 'Public' or \
                    self.honors[item.dest['id']].accessibility == '':
                mode_set.append([item])
        self.match_set.append({'Honor2Android/PublicInterfaceUseDep': mode_set})

    def test_find(self):
        tt = [[[-1, 'Class'], 'Contain', [-1, 'Class'], '01'], [[0, 1], 'Contain', [-1, 'Method'], '11'],
              [[1, 1], 'Call', [-1, 'Method'], '10'], [[0, 0], 'Contain', [2, 1], '00']]
        mode_set = []
        stack: List[Relation] = []
        state = 0

        def my_find(temp: list, graph, current):
            nonlocal mode_set
            src = graph[current][0]
            rel = graph[current][1]
            dest = graph[current][2]
            isHonor = graph[current][3]
            s = src[1] if src[0] == -1 else (temp[src[0]].dest['id'] if src[1] == 1 else temp[src[0]].src['id'])
            d = dest[1] if dest[0] == -1 else (temp[dest[0]].dest['id'] if dest[1] == 1 else temp[dest[0]].src['id'])
            for item in self.findSection(rel, isHonor, s, d):
                new_temp = temp[:]
                new_temp.append(item)
                if current < len(graph) - 1:
                    current += 1
                    my_find(new_temp, graph, current)
                    current -= 1
                else:
                    mode_set.append(new_temp)

        my_find(stack, tt, state)
        self.match_set.append({'users': mode_set})

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
        match_set_stat = self.get_static()
        match_set, union_temp, anti_patterns = self.ready_for_write()
        return match_set_stat, match_set, union_temp, anti_patterns

    def get_static(self):
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

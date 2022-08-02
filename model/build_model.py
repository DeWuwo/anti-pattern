import os.path
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.entity import Entity, set_package, set_parameters
from model.relation import Relation
from model.entity_owner import EntityOwner
from model.blamer.entity_tracer import BaseState, MethodState
from utils import Constant, FileCSV

MoveMethodRefactorings = [
    "Move And Rename Method",
    "Move Method",
    "Rename Method",
]

ExtractMethodRefactorings = [
    "Extract Method",
    "Extract And Move Method"
]

MoveMethodParamRefactorings = [
    "Rename Parameter",
    "Add Parameter",
    "Remove Parameter",
]

MoveClassRefactoring = [
    "Rename Class",
    "Move Class",
    "Move And Rename Class"
]


class BuildModel:
    # blame data
    entity_owner: EntityOwner
    # base info
    entity_android: List[Entity]
    entity_assi: List[Entity]
    relation_android: List[Relation]
    relation_assi: List[Relation]
    statistics_android: Dict
    statistics_assi: Dict
    # more info
    hidden_entities: List[int]
    hidden_modify_entities: List[int]
    access_modify_entities: List[int]
    final_modify_entities: List[int]
    refactor_entities: List[int]
    diff_relations: List[Relation]
    define_relations: List[Relation]
    reflect_relation: List[Relation]
    # query set
    query_map: defaultdict

    owner_proc: List[Dict]
    owner_proc_count: dict

    def __init__(self, entities_assi, cells_assi, statistics_assi: Dict, entities_android, cells_android,
                 statistics_android: Dict, entity_owner: EntityOwner):
        # first init
        self.entity_owner = entity_owner
        self.entity_android = []
        self.entity_assi = []
        self.relation_android = []
        self.relation_assi = []
        self.statistics_android = statistics_android
        self.statistics_assi = statistics_assi
        # self.hidden_entities = []
        self.hidden_modify_entities = []
        self.access_modify_entities = []
        self.final_modify_entities = []
        self.refactor_entities = []
        self.diff_relations = []
        self.define_relations = []
        self.reflect_relation = []
        self.owner_proc = []
        self.owner_proc_count = {}

        # init entity
        print("start init model entities")
        aosp_entity_set = defaultdict(partial(defaultdict, list))
        assi_entity_set = defaultdict(partial(defaultdict, list))
        # aosp entities
        print('     get aosp entities')
        for item in entities_android:
            if not item['external']:
                entity = Entity(**item)
                set_parameters(entity, self.entity_android)
                self.entity_android.append(entity)
                aosp_entity_set[entity.category][entity.qualifiedName].append(entity.id)

        # assi entities
        print('     get assi entities')
        for item in entities_assi:
            if not item['external']:
                entity = Entity(**item)
                # get entity package
                set_package(entity, self.entity_assi)
                set_parameters(entity, self.entity_assi)
                self.entity_assi.append(entity)
                assi_entity_set[entity.category][entity.qualifiedName].append(entity.id)

        # init dep
        print("start init model deps")
        relation_set = defaultdict(partial(defaultdict, partial(defaultdict, int)))
        print("     get aosp dep")
        for item in cells_android:
            relation = Relation(**item)
            self.relation_android.append(relation)
            relation_set[item['src']][relation.rel][item['dest']] = 1
        print("     get assi dep")
        temp_param = defaultdict(list)
        temp_define = defaultdict(list)
        for item in cells_assi:
            relation = Relation(**item)
            self.relation_assi.append(relation)
            if relation.rel == Constant.param:
                temp_param[relation.src].append(self.entity_assi[relation.dest])
            elif relation.rel == Constant.define:
                temp_define[relation.src].append(self.entity_assi[relation.dest])

        # data get -- blame
        print('start init owner from blame')
        all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = self.get_blame_data()
        print('get possible refactor entity')
        possible_refactor_entities = []
        possible_refactor_entities.extend(intrusive_entities.values())
        possible_refactor_entities.extend(old_intrusive_entities.values())
        possible_refactor_entities.extend(pure_accompany_entities.values())
        refactor_list = self.entity_owner.re_divide_owner(possible_refactor_entities)
        print('get entity owner')
        # first get entity owner
        print('     first get entity owner')
        not_sure_entities = self.first_owner(aosp_entity_set, assi_entity_set, all_native_entities, old_native_entities,
                                             old_update_entities, intrusive_entities, old_intrusive_entities,
                                             pure_accompany_entities, refactor_list, temp_define, temp_param)
        # print('     output entities owner unsure')
        # self.entity_owner.dump_ent_commit_infos(not_sure_entities)
        # # assi entities owner re sure
        # print('     get unsure entities refactoring info')
        # move_list = self.entity_owner.re_divide_owner(not_sure_entities)
        # print('     get refactoring entity owner')
        # self.resign_owner(not_sure_entities, move_list, temp_param, temp_define, aosp_entity_set, assi_entity_set,
        #                   intrusive_entities.keys())
        print('     output entities owner and intrusive info')
        self.out_intrusive_info()

        print('get filter relation set')
        for relation in self.relation_assi:
            self.set_dep_assi(relation, relation_set)

        # query set build
        print('get relation search dictionary')
        self.query_map_build(self.diff_relations, self.define_relations)

    # Get data of blame
    def get_blame_data(self):
        return self.entity_owner.divide_owner()

    # get diff and extra useful aosp 'define' dep
    def set_dep_assi(self, relation: Relation, rel_set: defaultdict):
        src = self.entity_assi[relation.src].entity_mapping
        dest = self.entity_assi[relation.dest].entity_mapping
        if not rel_set[src][relation.rel][dest]:
            relation.set_not_aosp(1)
            self.diff_relations.append(relation)
        elif relation.rel == Constant.define:
            self.define_relations.append(relation)

    # get owner string '01', '10', '11' or '00'
    def get_direction(self, relation: Relation):
        return str(self.entity_assi[relation.src].not_aosp) + str(self.entity_assi[relation.dest].not_aosp)

    # Construction of query map
    def query_map_build(self, diff: List[Relation], android_define_set: List[Relation]):
        self.query_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        for item in diff:
            self.query_map[item.rel][self.get_direction(item)][self.entity_assi[item.src].category][
                self.entity_assi[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][self.entity_assi[item.src].category][
                item.dest].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][
                self.entity_assi[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][item.dest].append(item)
        for item in android_define_set:
            self.query_map[item.rel]['00'][self.entity_assi[item.src].category][
                self.entity_assi[item.dest].category].append(item)

            self.query_map[item.rel]['00'][self.entity_assi[item.src].category][item.dest].append(item)

            self.query_map[item.rel]['00'][item.src][self.entity_assi[item.dest].category].append(item)
            self.query_map[item.rel]['00'][item.src][item.dest].append(item)

    # query method
    def query_relation(self, rel: str, not_aosp: str, src, dest) -> List[Relation]:
        return self.query_map[rel][not_aosp][src][dest]

    def diff_map_aosp(self, entity: Entity, search_name: str, aosp_entity_set: defaultdict,
                      assi_entity_set: defaultdict):
        aosp_list: List[int] = aosp_entity_set[entity.category][search_name]
        assi_list: List[int] = assi_entity_set[entity.category][entity.qualifiedName]
        if not aosp_list:
            return 0
        else:
            if len(aosp_list) == 1:
                if len(assi_list) == 1:
                    self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                    return 1
                else:
                    if entity.category == Constant.E_class and entity.anonymous != -1:
                        if self.entity_android[aosp_list[0]].raw_type == entity.raw_type and \
                                self.entity_android[self.entity_android[aosp_list[0]].anonymous].name == \
                                self.entity_assi[entity.anonymous].name:
                            self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                            return 1
                    elif Constant.anonymous_class in entity.qualifiedName:
                        if self.diff_map_aosp(self.entity_assi[entity.parentId],
                                              self.entity_assi[entity.parentId].qualifiedName, aosp_entity_set,
                                              assi_entity_set):
                            self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                            return 1
                    # 新增了重载方法的情况
                    elif self.entity_android[aosp_list[0]].parameter_types == entity.parameter_types:
                        self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                        return 1
                    return 0
            else:
                for item_id in aosp_list:
                    if entity.category == Constant.E_class and entity.anonymous != -1:
                        if self.entity_android[item_id].raw_type == entity.raw_type and \
                                self.entity_android[self.entity_android[item_id].anonymous].name == \
                                self.entity_assi[entity.anonymous].name:
                            self.get_entity_map(entity, self.entity_android[item_id])
                            return 1
                    elif Constant.anonymous_class in entity.qualifiedName:
                        if self.diff_map_aosp(self.entity_assi[entity.parentId],
                                              self.entity_assi[entity.parentId].qualifiedName, aosp_entity_set,
                                              assi_entity_set):
                            self.get_entity_map(entity, self.entity_android[item_id])
                            return 1
                    elif self.entity_android[item_id].parameter_types == entity.parameter_types:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return 1
                return 0

    # diff & blame
    def first_owner(self, aosp_entity_map, assi_entity_map, all_native_entities: dict, old_native_entities: dict,
                    old_update_entities: dict, intrusive_entities: dict, old_intrusive_entities: dict,
                    pure_accompany_entities: dict, refactor_list: Dict[int, list], child_define: Dict[int, List[Entity]],
                    child_param: dict) -> List:
        not_sure_entity_list = []
        keys_intrusive_entities = intrusive_entities.keys()
        keys_old_intrusive_entities = old_intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_old_native_entities = old_native_entities.keys()
        keys_old_update_entities = old_update_entities.keys()
        keys_all_native_entities = all_native_entities.keys()
        self.owner_proc_count = {
            'dep_coupling': 0,
            'dep_native': 0,
            'dep_extension': 0,
            'git_native': 0,
            'git_old_native': 0,
            'git_old_update': 0,
            'git_intrusive': 0,
            'git_old_intrusive': 0,
            'git_extension': 0,
            'dep_native_git_native': 0,
            'dep_native2git_old_native': 0,
            'dep_native2git_old_native_c': [0, 0, 0],
            'dep_native2git_old_update': 0,
            'dep_native2git_old_update_c': [0, 0, 0],
            'dep_native2git_intrusive': 0,
            'dep_native2git_intrusive_c': [0, 0, 0],
            'dep_native2git_old_intrusive': 0,
            'dep_native2git_old_intrusive_c': [0, 0, 0],
            'dep_native2git_extension': 0,
            'dep_native2git_extension_c': [0, 0, 0],
            'dep_extension_git_extension': 0,
            'dep_extension2git_native': 0,
            'dep_extension2git_native_c': [0, 0, 0],
            'dep_extension2git_old_native': 0,
            'dep_extension2git_old_native_c': [0, 0, 0],
            'dep_extension2git_old_update': 0,
            'dep_extension2git_old_update_c': [0, 0, 0],
            'dep_extension2git_intrusive': 0,
            'dep_extension2git_intrusive_c': [0, 0, 0],
            'dep_extension2git_old_intrusive': 0,
            'dep_extension2git_old_intrusive_c': [0, 0, 0],
            "Move And Rename Method": 0,
            "Move Method": 0,
            "Rename Method": 0,
            "Extract Method": 0,
            "Extract And Move Method": 0,
            "Rename Parameter": 0,
            "Add Parameter": 0,
            "Remove Parameter": 0,
            "Rename Class": 0,
            "Move Class": 0,
            "Move And Rename Class": 0
        }

        def get_index(category: str) -> int:
            if category == Constant.E_class or category == Constant.E_interface:
                return 0
            elif category == Constant.E_method:
                return 1
            elif category == Constant.E_variable:
                return 2

        def detect_ownership(ent: Entity, all_refactor_info: Dict[int, list], src_name: str, src_param: str):
            try:
                ent_refactor_info = all_refactor_info[ent.id][1]
                if "android.view.WindowManagerPolicyControl" in ent.qualifiedName:
                    print('  detect ref', ent.qualifiedName, src_name, src_param)
                detect_refactor_entities(ent, ent_refactor_info, all_refactor_info)
            except KeyError:
                if "android.view.WindowManagerPolicyControl" in ent.qualifiedName:
                    print('  detect not ref', ent.qualifiedName, src_name, src_param)
                detect_un_refactor_entities(ent, src_name, src_param)

        def detect_refactor_entities(ent: Entity, ent_refactor_info: list, all_refactor_info: Dict[int, list]):
            def detect_refactor_entities_son(child_entity_set: List[Entity], outer_ref_name: str, outer_ref_param: str):
                for child_ent in child_entity_set:
                    child_source_qualified_name = outer_ref_name + '.' + child_ent.name
                    if child_ent.category == Constant.E_method:
                        child_source_param = child_ent.parameter_names
                    else:
                        child_source_param = outer_ref_param
                    if "com.android.server.policy.PolicyControl" in child_source_qualified_name:
                        print(" detect son", child_ent.qualifiedName, child_source_qualified_name, child_source_param)
                    detect_ownership(child_ent, all_refactor_info, child_source_qualified_name, child_source_param)
                    detect_refactor_entities_son(child_define[child_ent.id] + child_param[child_ent.id],
                                                 child_source_qualified_name, child_source_param)

            for move in ent_refactor_info:
                move_type: str = move[0]
                source_state: BaseState = move[1]
                dest_state: BaseState = move[2]
                print(move_type, source_state.longname(), dest_state.longname())
                if not self.graph_differ(ent, source_state.longname(), source_state.get_param(), aosp_entity_map,
                                         assi_entity_map) and ent.id in keys_pure_accompany_entities:
                    ent.set_honor(1)
                    continue
                if move_type in MoveClassRefactoring:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    ent.set_refactor(
                        {'type': move_type, 'value': source_state.longname()})
                    self.refactor_entities.append(ent.id)
                    self.owner_proc_count[move_type] += 1
                    print(' ready to detect son', source_state.longname(), source_state.get_param())
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in MoveMethodRefactorings:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    ent.set_refactor(
                        {'type': move_type, 'value': source_state.longname()})
                    self.refactor_entities.append(ent.id)
                    self.owner_proc_count[move_type] += 1
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in ExtractMethodRefactorings:
                    ent.set_honor(1)
                    for ent in child_param[ent.id]:
                        ent.set_honor(1)
                    ent.set_refactor(
                        {'type': move_type, 'value': source_state.longname()})
                    self.refactor_entities.append(ent.id)
                    self.owner_proc_count[move_type] += 1
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in MoveMethodParamRefactorings:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    ent.set_refactor(
                        {'type': move_type, 'value': source_state.longname()})
                    self.refactor_entities.append(ent.id)
                    self.owner_proc_count[move_type] += 1
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param())
                else:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    ent.set_refactor(
                        {'type': move_type, 'value': source_state.longname()})

        def detect_un_refactor_entities(ent: Entity, source_name: str, source_param: str):
            if ent.not_aosp != -1:
                return
            dep_diff_res = self.graph_differ(ent, source_name, source_param, aosp_entity_map,
                                             assi_entity_map)
            if "android.view.WindowManagerPolicyControl" in ent.qualifiedName:
                print('  detect not ref', ent.id, source_name, source_param, dep_diff_res)
            if dep_diff_res:
                if ent.id in keys_old_native_entities or ent.id in keys_old_update_entities:
                    ent.set_honor(0)
                    ent.set_old_aosp(1)
                elif ent.id in keys_intrusive_entities or ent.id in keys_old_intrusive_entities:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                elif ent.id in keys_pure_accompany_entities:
                    ent.set_honor(0)
                    # 修改覆盖所有行
                else:
                    ent.set_honor(0)
            else:
                if ent.id in keys_old_native_entities:
                    ent.set_honor(0)
                    ent.set_old_aosp(2)
                elif ent.id in keys_old_intrusive_entities:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                elif ent.id in keys_pure_accompany_entities:
                    ent.set_honor(1)
                    # 修改覆盖所有行
                else:
                    ent.set_honor(1)

        for entity in self.entity_assi:
            proc = entity.to_csv()
            proc['modify_to'] = 'null'
            # 解耦仓实体
            if entity.is_decoupling > 1:
                entity.set_honor(1)
                proc['dep_diff'] = '1-coupling'
                self.owner_proc_count['dep_coupling'] += 1
            else:
                detect_ownership(entity, refactor_list, entity.qualifiedName, entity.parameter_names)

            # diff 识别为原生的实体，一定正确
            # elif self.diff_map_aosp(entity, entity.qualifiedName, aosp_entity_map, assi_entity_map):
            #     # diff = aosp
            #     entity.set_honor(0)
            #     proc['dep_diff'] = '0'
            #     self.owner_proc_count['dep_native'] += 1
            #     if entity.id in keys_intrusive_entities:
            #         not_sure_entity_list.append(intrusive_entities[entity.id])
            #         entity.set_intrusive(1)
            #         self.owner_proc_count['dep_native2git_intrusive'] += 1
            #         self.owner_proc_count['dep_native2git_intrusive_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_intrusive_entities:
            #         not_sure_entity_list.append(old_intrusive_entities[entity.id])
            #         entity.set_intrusive(1)
            #         self.owner_proc_count['dep_native2git_old_intrusive'] += 1
            #         self.owner_proc_count['dep_native2git_old_intrusive_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_native_entities:
            #         entity.set_old_aosp(1)
            #         self.owner_proc_count['dep_native2git_old_native'] += 1
            #         self.owner_proc_count['dep_native2git_old_native_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_update_entities:
            #         entity.set_old_aosp(1)
            #         self.owner_proc_count['dep_native2git_old_update'] += 1
            #         self.owner_proc_count['dep_native2git_old_update_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_pure_accompany_entities:
            #         not_sure_entity_list.append(pure_accompany_entities[entity.id])
            #         self.owner_proc_count['dep_native2git_extension'] += 1
            #         self.owner_proc_count['dep_native2git_extension_c'][get_index(entity.category)] += 1
            #     else:
            #         self.owner_proc_count['dep_native_git_native'] += 1
            # else:
            #     proc['dep_diff'] = '1'
            #     self.owner_proc_count['dep_extension'] += 1
            #     # git blame 识别为原生的实体，一定正确
            #     if entity.id in keys_all_native_entities:
            #         entity.set_honor(0)
            #         self.owner_proc_count['dep_extension2git_native'] += 1
            #         self.owner_proc_count['dep_extension2git_native_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_native_entities:
            #         entity.set_honor(0)
            #         entity.set_old_aosp(1)
            #         self.owner_proc_count['dep_extension2git_old_native'] += 1
            #         self.owner_proc_count['dep_extension2git_old_native_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_update_entities:
            #         entity.set_honor(0)
            #         entity.set_old_aosp(1)
            #         self.owner_proc_count['dep_extension2git_old_update'] += 1
            #         self.owner_proc_count['dep_extension2git_old_update_c'][get_index(entity.category)] += 1
            #     # diff = blame = assi
            #     elif entity.id in keys_pure_accompany_entities:
            #         not_sure_entity_list.append(pure_accompany_entities[entity.id])
            #         entity.set_honor(1)
            #         self.owner_proc_count['dep_extension_git_extension'] += 1
            #     # diff = assi != blame = (aosp or ins) 此时一定在all_entities中，即该实体所在文件被第三方修改过
            #     elif entity.id in keys_intrusive_entities:
            #         not_sure_entity_list.append(intrusive_entities[entity.id])
            #         proc['modify_to'] = 'unsure'
            #         self.owner_proc_count['dep_extension2git_intrusive'] += 1
            #         self.owner_proc_count['dep_extension2git_intrusive_c'][get_index(entity.category)] += 1
            #     elif entity.id in keys_old_update_entities:
            #         not_sure_entity_list.append(old_intrusive_entities[entity.id])
            #         proc['modify_to'] = 'unsure'
            #         self.owner_proc_count['dep_extension2git_old_intrusive'] += 1
            #         self.owner_proc_count['dep_extension2git_old_intrusive_c'][get_index(entity.category)] += 1
            #     else:
            #         entity.set_honor(0)
            #         self.owner_proc_count['dep_extension2git_native'] += 1
            #         self.owner_proc_count['dep_extension2git_native_c'][get_index(entity.category)] += 1
            # self.owner_proc.append(proc)
        return not_sure_entity_list

    # 通过refactoring miner再次识别
    def resign_owner(self, not_sure_entities: List[dict], move_list: Dict[int, list], param_entities: defaultdict,
                     define_entities: defaultdict, aosp_entity_set: defaultdict, assi_entity_set: defaultdict,
                     intrusive_entities):

        def rename_map(rename_entity: Entity, search_qualified_name: str):
            aosp_list: List[int] = aosp_entity_set[rename_entity.category][search_qualified_name]
            if aosp_list:
                self.get_entity_map(rename_entity, self.entity_android[aosp_list[0]])
            else:
                rename_entity.set_old_aosp(1)

        for entity in not_sure_entities:
            refactor_entity = self.entity_assi[int(entity['id'])]
            if refactor_entity.is_core_entity():
                try:
                    moves = move_list[int(entity['id'])][1]
                    for move in moves:
                        move_type = move[0]
                        source_name = move[1]
                        dest_name = move[2]
                        print('   ', move_type, source_name.longname(), dest_name.longname())
                        if move_type in MoveClassRefactoring:
                            refactor_entity.set_honor(0)
                            refactor_entity.set_intrusive(1)
                            self.refactor_entities.append(int(entity['id']))
                            self.owner_proc_count['rename'][0] += 1
                            self.entity_assi[int(entity['id'])].set_refactor(
                                {'type': move_type, 'value': source_name.longname()})
                            rename_map(self.entity_assi[int(entity['id'])], source_name.longname())
                            for ent in param_entities[int(entity['id'])] + define_entities[int(entity['id'])]:
                                source_qualified_name = source_name.longname() + '.' + ent.name
                                print('     param', source_qualified_name)
                                owner = 0 if self.diff_map_aosp(ent, source_qualified_name, aosp_entity_set,
                                                                assi_entity_set) else 1
                                ent.set_honor(owner)
                        elif move_type in MoveMethodRefactorings:
                            refactor_entity.set_honor(0)
                            refactor_entity.set_intrusive(1)
                            self.refactor_entities.append(int(entity['id']))
                            self.owner_proc_count['rename'][0] += 1
                            self.entity_assi[int(entity['id'])].set_refactor(
                                {'type': move_type, 'value': source_name.longname()})
                            rename_map(self.entity_assi[int(entity['id'])], source_name.longname())
                            for ent in param_entities[int(entity['id'])] + define_entities[int(entity['id'])]:
                                source_qualified_name = source_name.longname() + '.' + ent.name
                                print('     param', source_qualified_name)
                                owner = 0 if self.diff_map_aosp(ent, source_qualified_name, aosp_entity_set,
                                                                assi_entity_set) else 1
                                ent.set_honor(owner)
                    else:
                        self.entity_assi[int(entity['id'])].set_honor(1)
                except KeyError:
                    self.entity_assi[int(entity['id'])].set_honor(1)
            else:
                self.entity_assi[int(entity['id'])].set_honor(1)

    def load_owner_from_catch(self):
        owners = FileCSV.read_from_file_csv(os.path.join(self.entity_owner.out_path, 'final_ownership.csv'))
        for owner in owners:
            self.entity_assi[int(owner[0])].set_honor(int(owner[1]))
            self.entity_assi[int(owner[0])].set_honor(int(owner[5]))

    # graph differ
    def graph_differ(self, entity: Entity, search_name: str, search_param: str, aosp_entity_set: defaultdict,
                     assi_entity_set: defaultdict):
        aosp_list: List[int] = aosp_entity_set[entity.category][search_name]
        assi_list: List[int] = assi_entity_set[entity.category][entity.qualifiedName]
        if not aosp_list:
            return 0
        elif len(aosp_list) == 1 and len(assi_list) == 1:
            self.get_entity_map(entity, self.entity_android[aosp_list[0]])
            return aosp_list[0]
        else:
            if entity.category == Constant.E_class and entity.anonymous != -1:
                for item_id in aosp_list:
                    if self.entity_android[item_id].raw_type == entity.raw_type and \
                            self.entity_android[self.entity_android[item_id].anonymous].name == \
                            self.entity_assi[entity.anonymous].name:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_class or entity.category == Constant.E_interface:
                self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                return aosp_list[0]
            elif Constant.anonymous_class in entity.qualifiedName:
                for item_id in aosp_list:
                    if get_parent_entity(item_id, self.entity_android).id == self.graph_differ(
                            self.entity_assi[entity.parentId],
                            self.entity_assi[entity.parentId].qualifiedName,
                            self.entity_assi[entity.parentId].parameter_names,
                            aosp_entity_set, assi_entity_set):
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return 1
            elif entity.category == Constant.E_method or entity.category == Constant.E_variable:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_names == search_param:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return 1
            else:
                return 1
            return 0

    # Get entity mapping relationship
    def get_entity_map(self, assi_entity: Entity, native_entity: Entity):
        assi_entity.set_entity_mapping(native_entity.id)
        native_entity.set_entity_mapping(assi_entity.id)
        # storage special entities
        if assi_entity.hidden:
            source_hd = Constant.hidden_map(native_entity.hidden)
            update_hd = Constant.hidden_map(assi_entity.hidden)
            if source_hd != update_hd:
                self.hidden_modify_entities.append(assi_entity.id)
                assi_entity.set_hidden_modify(source_hd + '--' + update_hd)
        if assi_entity.modifiers != native_entity.modifiers:
            if assi_entity.accessible != native_entity.accessible:
                assi_entity.set_intrusive(1)
                self.access_modify_entities.append(assi_entity.id)
                assi_entity.set_access_modify(native_entity.accessible + '-' + assi_entity.accessible)
            if not assi_entity.final and native_entity.final:
                assi_entity.set_intrusive(1)
                self.final_modify_entities.append(assi_entity.id)

    # out intrusive entities info
    def out_intrusive_info(self):
        FileCSV.write_owner_to_csv(self.entity_owner.out_path, 'final_ownership', self.entity_assi)
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'owner_proc', self.owner_proc)
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'owner_proc_count', [self.owner_proc_count])
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'access_modify_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.access_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'final_modify_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.final_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'refactor_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.refactor_entities],
                                    'modify')


# valid entity map
def valid_entity_mapping(entity: Entity, search_name: str, search_param: str):
    return entity.qualifiedName == search_name and entity.parameter_names == search_param


# get parent
def get_parent_entity(entity: int, entity_set: List[Entity]):
    return entity_set[entity_set[entity].parentId]

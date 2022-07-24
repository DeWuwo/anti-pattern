import os.path
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.entity import Entity, set_package, set_parameters
from model.relation import Relation
from model.entity_owner import EntityOwner, get_rename_source
from utils import Constant, FileCSV


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
            elif self.entity_assi[relation.src].category == Constant.E_method and relation.rel == Constant.define:
                temp_define[relation.src].append(self.entity_assi[relation.dest])

        # data get -- blame
        print('start init owner from blame')
        all_entities, intrusive_entities, pure_accompany_entities = self.get_blame_data()
        print('get entity owner')
        # first get entity owner
        print('     first get entity owner')
        not_sure_entities = self.first_owner(aosp_entity_set, assi_entity_set, all_entities, intrusive_entities,
                                             pure_accompany_entities)
        print('     output entities owner unsure')
        self.entity_owner.dump_ent_commit_infos(not_sure_entities)
        # assi entities owner re sure
        print('     get unsure entities refactoring info')
        move_list = self.entity_owner.re_divide_owner(not_sure_entities)
        print('     get refactoring entity owner')
        self.resign_owner(not_sure_entities, move_list, temp_param, temp_define, aosp_entity_set, assi_entity_set,
                          intrusive_entities.keys())
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
            if len(aosp_list) == 1 and len(assi_list) == 1:
                self.get_entity_map(entity, self.entity_android[aosp_list[0]])
                return 1
            else:
                for item_id in aosp_list:
                    if entity.category == Constant.E_class and entity.anonymous != -1:
                        if self.entity_android[item_id].raw_type == entity.raw_type and \
                                self.entity_android[item_id].name == self.entity_assi[entity.anonymous].name:
                            self.get_entity_map(entity, self.entity_android[item_id])
                            return 1
                        return 0
                    elif Constant.anonymous_class in entity.qualifiedName:
                        return self.diff_map_aosp(self.entity_assi[entity.parentId],
                                                  self.entity_assi[entity.parentId].qualifiedName, aosp_entity_set,
                                                  assi_entity_set)
                    if self.entity_android[item_id].parameter_types == entity.parameter_types:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return 1
                return 0

    # diff & blame
    def first_owner(self, aosp_entity_map, assi_entity_map, all_entities: dict, intrusive_entities: dict,
                    pure_accompany_entities: dict) -> List:
        not_sure_entity_list = []
        keys_intrusive_entities = intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_all_entities = all_entities.keys()
        self.owner_proc_count = {
            'dep_coupling': 0,
            'dep_native': 0,
            'dep_extension': 0,
            'git_native': 0,
            'git_intrusive': 0,
            'git_extension': 0,
            'dep_native_git_native': 0,
            'dep_native2git_intrusive': 0,
            'dep_native2git_extension': 0,
            'dep_native2git_extension_c': [0, 0, 0],
            'dep_extension_git_extension': 0,
            'dep_extension2git_native': 0,
            'dep_extension2git_native_c': [0, 0, 0],
            'dep_extension2git_intrusive': 0,
            'dep_extension2git_intrusive_c': [0, 0, 0],
            'rename': [0, 0]
        }

        def get_index(category: str) -> int:
            if category == Constant.E_class:
                return 0
            elif category == Constant.E_method:
                return 1
            else:
                return 2

        for entity in self.entity_assi:
            proc = entity.to_csv()
            proc['modify_to'] = 'null'
            if entity.id in keys_intrusive_entities:
                proc['git_blame'] = '0.5'
                self.owner_proc_count['git_intrusive'] += 1
            elif entity.id in keys_pure_accompany_entities:
                proc['git_blame'] = '1'
                self.owner_proc_count['git_extension'] += 1
            elif entity.is_decoupling <= 1:
                proc['git_blame'] = '0'
                self.owner_proc_count['git_native'] += 1
            # 解耦仓实体
            if entity.is_decoupling > 1:
                entity.set_honor(1)
                proc['dep_diff'] = '1-coupling'
                self.owner_proc_count['dep_coupling'] += 1
            # diff 识别为原生的实体，一定正确
            elif self.diff_map_aosp(entity, entity.qualifiedName, aosp_entity_map, assi_entity_map):
                # diff = aosp
                entity.set_honor(0)
                proc['dep_diff'] = '0'
                self.owner_proc_count['dep_native'] += 1
                if entity.id in keys_intrusive_entities:
                    entity.set_intrusive(1)
                    proc['modify_to'] = '0.5'
                    self.owner_proc_count['dep_native2git_intrusive'] += 1
                elif entity.id in keys_pure_accompany_entities:
                    self.owner_proc_count['dep_native2git_extension'] += 1
                    self.owner_proc_count['dep_native2git_extension_c'][get_index(entity.category)] += 1
                else:
                    self.owner_proc_count['dep_native_git_native'] += 1
            else:
                proc['dep_diff'] = '1'
                self.owner_proc_count['dep_extension'] += 1
                # git blame 识别为原生的实体，一定正确
                if entity.id not in keys_all_entities or \
                        ((entity.id not in keys_pure_accompany_entities) and
                         (entity.id not in keys_intrusive_entities)):
                    entity.set_honor(0)
                    proc['modify_to'] = '0'
                    self.owner_proc_count['dep_extension2git_native'] += 1
                    self.owner_proc_count['dep_extension2git_native_c'][get_index(entity.category)] += 1
                # diff = blame = assi
                elif entity.id in pure_accompany_entities:
                    entity.set_honor(1)
                    self.owner_proc_count['dep_extension_git_extension'] += 1
                # diff = assi != blame = (aosp or ins) 此时一定在all_entities中，即该实体所在文件被第三方修改过
                else:
                    not_sure_entity_list.append(all_entities[entity.id])
                    proc['modify_to'] = 'unsure'
                    self.owner_proc_count['dep_extension2git_intrusive'] += 1
                    self.owner_proc_count['dep_extension2git_intrusive_c'][get_index(entity.category)] += 1
            self.owner_proc.append(proc)
        return not_sure_entity_list

    # 通过refactoring miner再次识别
    def resign_owner(self, not_sure_entities: List[dict], move_list: dict, param_entities: defaultdict,
                     define_entities: defaultdict, aosp_entity_set: defaultdict, assi_entity_set: defaultdict,
                     intrusive_entities):

        def rename_map(rename_entity: Entity, search_qualified_name: str):
            aosp_list: List[int] = aosp_entity_set[rename_entity.category][search_qualified_name]
            if aosp_list:
                self.get_entity_map(rename_entity, self.entity_android[aosp_list[0]])
            else:
                rename_entity.set_honor(1)

        for entity in not_sure_entities:
            refactor_entity = self.entity_assi[int(entity['id'])]
            if refactor_entity.is_core_entity():
                try:
                    moves = move_list[int(entity['id'])]['Moves']
                    move_types = []
                    move_types_map = {}
                    for index, move in enumerate(moves):
                        move_types.append(move['type'])
                        move_types_map[move['type']] = index
                    # 主要处理重命名重构，其他重构认为伴生
                    if int(entity['id']) in intrusive_entities and 'Rename Method' in move_types:
                        refactor_entity.set_honor(0)
                        refactor_entity.set_intrusive(1)
                        self.refactor_entities.append(int(entity['id']))
                        self.owner_proc_count['rename'][0] += 1
                        source_name = get_rename_source(
                            moves[move_types_map['Rename Method']]['leftSideLocations'][0]["codeElement"])
                        self.entity_assi[int(entity['id'])].set_refactor(
                            {'type': 'Rename Method', 'value': source_name})
                        print('                 rename-m', source_name)
                        source_qualified_name = refactor_entity.qualifiedName.rsplit('.', 1)[0] + '.' + source_name
                        rename_map(self.entity_assi[int(entity['id'])], source_qualified_name)
                        for ent in param_entities[int(entity['id'])] + define_entities[int(entity['id'])]:
                            name_list = ent.qualifiedName.rsplit('.', 2)
                            name_list[1] = source_name
                            source_qualified_name = '.'.join(name_list)
                            owner = 0 if self.diff_map_aosp(ent, source_qualified_name, aosp_entity_set,
                                                            assi_entity_set) else 1
                            ent.set_honor(owner)
                    elif int(entity['id']) in intrusive_entities and 'Rename Class' in move_types:
                        self.entity_assi[int(entity['id'])].set_honor(0)
                        self.entity_assi[int(entity['id'])].set_intrusive(1)
                        self.owner_proc_count['rename'][1] += 1
                        self.refactor_entities.append(int(entity['id']))
                        source_name: str = moves[move_types_map['Rename Class']]['leftSideLocations'][0][
                            "codeElement"]
                        self.entity_assi[int(entity['id'])].set_refactor({'type': 'Rename Class', 'value': source_name})
                        print('                 rename-m', source_name)
                        rename_map(self.entity_assi[int(entity['id'])], source_name.rsplit('.', 1)[1])
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

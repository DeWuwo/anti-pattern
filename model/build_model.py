from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.entity import Entity, set_package, set_parameters
from model.relation import Relation
from model.entity_owner import EntityOwner, get_rename_source
from utils import Constant


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
    diff_relations: List[Relation]
    define_relations: List[Relation]
    reflect_relation: List[Relation]
    # query set
    query_map: defaultdict

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
        self.diff_relations = []
        self.define_relations = []
        self.reflect_relation = []
        # data get -- blame
        print('start init owner from blame')
        all_entities, intrusive_entities, pure_accompany_entities = self.get_blame_data()
        # init entity
        print("start init model entities")
        aosp_entity_set = defaultdict(partial(defaultdict, list))
        assi_entity_set = defaultdict(partial(defaultdict, list))
        # aosp entities
        print('     get aosp entities')
        for item in entities_android:
            if not item['external']:
                entity = Entity(**item)
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
        # first get entity owner
        print('     first get entity owner')
        not_sure_entities = self.first_owner(aosp_entity_set, assi_entity_set, all_entities, intrusive_entities,
                                             pure_accompany_entities)
        print('     output entities owner unsure')
        self.entity_owner.dump_ent_commit_infos(not_sure_entities)
        # assi entities owner re sure
        print('         get move')
        move_list = self.entity_owner.re_divide_owner(not_sure_entities)
        print('         re get entity owner')
        self.resign_owner(not_sure_entities, move_list, aosp_entity_set, assi_entity_set, intrusive_entities.keys())

        # init dep
        print("start init model deps")
        relation_set = defaultdict(partial(defaultdict, partial(defaultdict, int)))
        print("     get aosp dep")
        for item in cells_android:
            relation = Relation(**item)
            self.relation_android.append(relation)
            relation_set[item['src']][relation.rel][item['dest']] = 1
        print("     get assi dep")
        for item in cells_assi:
            relation = Relation(**item)
            self.set_dep_assi(relation, relation_set)

        # query set build
        self.query_map_build(self.diff_relations, self.define_relations)

    # Get data of blame
    def get_blame_data(self):
        return self.entity_owner.divide_owner()

    # get diff and extra useful aosp 'define' dep
    def set_dep_assi(self, relation: Relation, rel_set: defaultdict):
        diff_set: List[Relation] = []
        define_set: List[Relation] = []
        src = self.entity_assi[relation.src].entity_mapping
        dest = self.entity_assi[relation.dest].entity_mapping
        if not rel_set[src][relation.rel][dest]:
            relation.set_not_aosp(1)
            self.diff_relations.append(relation)
        elif relation.rel == Constant.define:
            self.define_relations.append(relation)
        return diff_set, define_set

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

    def diff_map_aosp(self, entity: Entity, aosp_entity_set: defaultdict, assi_entity_set: defaultdict):
        aosp_list: List[int] = aosp_entity_set[entity.category][entity.qualifiedName]
        assi_list: List[int] = assi_entity_set[entity.category][entity.qualifiedName]
        if not aosp_list:
            return 0
        else:
            if len(aosp_list) == 1:
                if len(assi_list) == 1:
                    get_entity_map(entity, self.entity_android[aosp_list[0]])
                    return 1
                else:
                    # 新增了重载方法的情况
                    if self.entity_android[aosp_list[0]].parameter_types == entity.parameter_types:
                        get_entity_map(entity, self.entity_android[aosp_list[0]])
                        return 1
                    return 0
            else:
                # 默认不会对重载方法进行参数列表修改
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_types == entity.parameter_types:
                        get_entity_map(entity, self.entity_android[item_id])
                        return 1
                return 0

    # diff & blame
    def first_owner(self, aosp_entity_map, assi_entity_map, all_entities: dict, intrusive_entities: dict,
                    pure_accompany_entities: dict) -> List:
        not_sure_entity_list = []
        keys_intrusive_entities = intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_all_entities = all_entities.keys()
        for entity in self.entity_assi:
            if entity.is_decoupling > 1:
                entity.set_honor(1)
            elif self.diff_map_aosp(entity, aosp_entity_map, assi_entity_map):
                # diff = blame = aosp
                if entity.above_file_level():
                    entity.set_honor(0)
                elif entity.id not in keys_pure_accompany_entities:
                    entity.set_honor(0)
                    if entity.id in keys_intrusive_entities:
                        entity.set_intrusive(1)
                    # storage special entities
                    temp = self.entity_android[entity.entity_mapping]
                    if entity.hidden:
                        source_hd = Constant.hidden_map(temp.hidden)
                        update_hd = Constant.hidden_map(entity.hidden)
                        if source_hd != update_hd:
                            self.hidden_modify_entities.append(entity.id)
                            entity.set_hidden_modify(source_hd.join('--').join(update_hd))
                    if entity.modifiers != temp.modifiers:
                        if entity.accessible != temp.accessible:
                            self.access_modify_entities.append(entity.id)
                        if not entity.final and temp.final:
                            self.final_modify_entities.append(entity.id)
                # diff = aosp != blame = assi(该情况应该是blame diff算法识别错误)
                else:
                    not_sure_entity_list.append(pure_accompany_entities[entity.id])
            else:
                # 保留旧版本代码情况
                if entity.id not in keys_all_entities or \
                        ((entity.id not in keys_pure_accompany_entities) and
                         (entity.id not in keys_intrusive_entities)):
                    entity.set_honor(0)
                # diff = blame = assi
                elif entity.id in pure_accompany_entities:
                    entity.set_honor(1)
                # diff = assi != blame = (aosp or ins) 此时一定在all_entities中，即该实体所在文件被第三方修改过
                else:
                    not_sure_entity_list.append(all_entities[entity.id])
        return not_sure_entity_list

    # 通过refactoring miner再次识别
    def resign_owner(self, not_sure_entities: List[dict], move_list: dict, aosp_entity_set: defaultdict,
                     assi_entity_set: defaultdict, intrusive_entities):

        def rename_map(rename_entity: Entity, method_name: str):
            source_qualified_name = rename_entity.qualifiedName.rsplit('.', 1)[0].join('.').join(method_name)
            aosp_list: List[int] = aosp_entity_set[rename_entity.category][source_qualified_name]
            if len(aosp_list) == 1:
                get_entity_map(rename_entity, self.entity_android[aosp_list[0]])
                return 1
            else:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_types == rename_entity.parameter_types:
                        get_entity_map(rename_entity, self.entity_android[item_id])
                        return 1
                return 0

        for entity in not_sure_entities:
            diff_aosp = self.diff_map_aosp(self.entity_assi[int(entity['id'])], aosp_entity_set, assi_entity_set)
            print(entity['id'])
            try:
                print('             move')
                moves = move_list[int(entity['id'])]['Moves']
                move_types = []
                move_types_map = {}
                for index, move in enumerate(moves):
                    move_types.append(move['type'])
                    move_types_map[move['type']] = index
                if not diff_aosp:
                    # 主要处理重命名重构，其他重构认为伴生
                    if int(entity['id']) in intrusive_entities and 'Rename Method' in move_types:
                        self.entity_assi[int(entity['id'])].set_honor(0)
                        self.entity_assi[int(entity['id'])].set_intrusive(1)
                        # print(moves[move_types_map['Rename Method']]['leftSideLocations'][0]["codeElement"])
                        source_name = get_rename_source(
                            moves[move_types_map['Rename Method']]['leftSideLocations'][0]["codeElement"])
                        print('                 rename-m', source_name)
                        rename_map(self.entity_assi[int(entity['id'])], source_name)
                    elif int(entity['id']) in intrusive_entities and 'Rename Class' in move_types:
                        self.entity_assi[int(entity['id'])].set_honor(0)
                        self.entity_assi[int(entity['id'])].set_intrusive(1)
                        source_name: str = moves[move_types_map['Rename Class']]['leftSideLocations'][0]["codeElement"]
                        print('                 rename-m', source_name)
                        rename_map(self.entity_assi[int(entity['id'])], source_name.rsplit('.', 1)[1])
                    else:
                        self.entity_assi[int(entity['id'])].set_honor(1)
                print('             move over')
            except KeyError:
                print('             un move')
                native_entity = self.entity_assi[int(entity['id'])]
                if diff_aosp:
                    # git blame识别错误，原生方法没有任何修改，且认为不会在重载方法中发生
                    native_entity.set_honor(0)
                    map_native_index = aosp_entity_set[native_entity.category][native_entity.qualifiedName][0]
                    get_entity_map(native_entity, self.entity_android[map_native_index])
                else:
                    self.entity_assi[int(entity['id'])].set_honor(1)
                print('             un move over')


# Get entity mapping relationship
def get_entity_map(assi_entity: Entity, native_entity: Entity):
    assi_entity.set_entity_mapping(native_entity.id)
    native_entity.set_entity_mapping(assi_entity.id)

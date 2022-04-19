from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.entity import Entity
from model.relation import Relation
from utils import Constant, FileReader


class BuildModel:
    # base info
    entity_android: List[Entity]
    entity_assi: List[Entity]
    relation_android: List[Relation]
    relation_assi: List[Relation]
    statistics_android: Dict
    statistics_assi: Dict
    # more info
    hidden_entities: List[Entity]
    access_modify_entities: List[Entity]
    final_modify_entities: List[Entity]
    diff_relations: List[Relation]
    define_relations: List[Relation]
    # query set
    query_map: defaultdict

    def __init__(self, entities_assi, cells_assi, statistics_assi: Dict, entities_android, cells_android,
                 statistics_android: Dict, intrusive_entities: List[int], assi_entities: List[int],
                 blame_null_entities: List[int]):
        # first init
        self.entity_android = []
        self.entity_assi = []
        self.relation_android = []
        self.relation_assi = []
        self.statistics_android = statistics_android
        self.statistics_assi = statistics_assi
        self.hidden_entities = []
        self.access_modify_entities = []
        self.final_modify_entities = []
        self.diff_relations = []
        self.define_relations = []
        # init entity
        print("start init model entities")
        entity: Entity
        entity_set = defaultdict(partial(defaultdict, list))
        for item in entities_android:
            if not item['external']:
                entity = Entity(**item)
                self.entity_android.append(entity)
                entity_set[entity.category][entity.qualifiedName].append(entity.id)
        compare1 = []
        compare2 = []
        compare3 = []
        for item in entities_assi:
            if not item['external']:
                entity = Entity(**item)
                if self.blame_stub(entity, entity_set):
                    entity.set_honor(0)
                    self.get_entity_map(entity, entity_set)
                else:
                    entity.set_honor(1)
                # if entity.id in assi_entities:
                #     entity.set_honor(1)
                #     if self.blame_stub(entity, entity_set):
                #         compare1.append(entity.toJson())
                # else:
                #     if entity.id in intrusive_entities:
                #         entity.set_intrusive(1)
                #     self.get_entity_map(entity, entity_set)
                #     if not self.blame_stub(entity, entity_set):
                #         if entity.id in blame_null_entities:
                #             compare2.append(entity.toJson())
                #         else:
                #             if entity.category != 'Variable':
                #                 compare3.append(entity.toJson())
                    # storage special entities
                    if entity.aosp_hidden:
                        self.hidden_entities.append(entity)
                    temp = self.entity_android[entity.entity_mapping]
                    if entity.modifiers != temp.modifiers:
                        if entity.accessible != temp.accessible:
                            self.access_modify_entities.append(entity)
                        if not entity.final and temp.final:
                            self.final_modify_entities.append(entity)
                self.entity_assi.append(entity)
        # FileReader.write_to_json('D:/Honor/experiment/lineage/4-19/base/compare',
        #                          {'b1': compare1, 'b2': compare2, 'b3': compare3}, 0)
        print(len(compare2))

        # init dep
        print("start init model deps")
        bind_var = -1
        relation_type = ''
        relation_set = defaultdict(partial(defaultdict, partial(defaultdict, int)))
        for item in cells_android:
            for key in item['values']:
                if key == 'bindVar':
                    bind_var = item['values'][key]
                else:
                    relation_type = key
            relation = Relation({'id': item['src']}, bind_var, relation_type, {'id': item['dest']})
            self.relation_android.append(relation)
            relation_set[item['src']][relation.rel][item['dest']] = 1
        for item in cells_assi:
            for key in item['values']:
                if key == 'bindVar':
                    bind_var = item['values'][key]
                else:
                    relation_type = key
            relation = Relation({'id': item['src']}, bind_var, relation_type, {'id': item['dest']})
            self.set_dep_assi(relation, relation_set)

        # query set build
        self.query_map_build(self.diff_relations, self.define_relations)

    # Get entity mapping relationship
    def get_entity_map(self, entity: Entity, android_entity_set: defaultdict):
        map_list = android_entity_set[entity.category][entity.qualifiedName]
        if len(map_list) >= 1:
            entity_id = map_list[0]
            entity.set_entity_mapping(entity_id)
            self.entity_android[entity_id].set_entity_mapping(entity.id)
        elif not map_list:
            if entity.is_intrusive:
                entity.set_honor(1)
            else:
                # 文件路径修改
                pass

    # get diff and extra useful aosp 'define' dep
    def set_dep_assi(self, relation: Relation, rel_set: defaultdict):
        diff_set: List[Relation] = []
        define_set: List[Relation] = []
        src = self.entity_assi[relation.src['id']].entity_mapping
        dest = self.entity_assi[relation.dest['id']].entity_mapping
        if not rel_set[src][relation.rel][dest]:
            relation.set_not_aosp(1)
            self.diff_relations.append(relation)
        elif relation.rel == Constant.define:
            self.define_relations.append(relation)
        return diff_set, define_set

    # get owner string '01', '10', '11' or '00'
    def get_direction(self, relation: Relation):
        return str(self.entity_assi[relation.src['id']].isHonor) + str(self.entity_assi[relation.dest['id']].isHonor)

    # Construction of query map
    def query_map_build(self, diff: List[Relation], android_define_set: List[Relation]):
        self.query_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        for item in diff:
            self.query_map[item.rel][self.get_direction(item)][self.entity_assi[item.src['id']].category][
                self.entity_assi[item.dest['id']].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][self.entity_assi[item.src['id']].category][
                item.dest['id']].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src['id']][
                self.entity_assi[item.dest['id']].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src['id']][item.dest['id']].append(item)
            # if item.bind_var != -1:
            #     self.query_map[item.bind_var][self.get_direction(item)][self.entity_assi[item.src['id']].category][
            #         self.entity_assi[item.dest['id']].category].append(item)
        for item in android_define_set:
            self.query_map[item.rel]['00'][item.src['id']][item.dest['id']].append(item)

    # query method
    def query_relation(self, rel: str, not_aosp: str, src, dest) -> List[Relation]:
        return self.query_map[rel][not_aosp][src][dest]

    def blame_stub(self, entity: Entity, android_entity_set: defaultdict):
        return android_entity_set[entity.category][entity.qualifiedName]

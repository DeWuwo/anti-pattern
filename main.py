import argparse
from typing import List
from collections import defaultdict
from utils import FileReader
from model.entity import Entity
from model.relation import Relation
from model.mode import ModeMatch
from model.build_model import BuildModel
from model.anti_pattern import AntiPattern
from model.match import Match

access_map = {'': '0', 'Private': '1', 'Protected': '2', 'Public': '3'}


def get_honor_entities(honor: List[Entity], android: List[Entity]):
    print('detecting entities...')
    entity_map = defaultdict(list)
    # deal entities
    for item in android:
        entity_map[item.__str__()].append(item.id)

    def find_same(entity: Entity):
        if len(entity_map[entity.__str__()]) == 1:
            return entity_map[entity.__str__()][0]
        elif len(entity_map[entity.__str__()]) == 0:
            return -1
        else:
            for android_entity in entity_map[entity.__str__()]:
                if android[android_entity].modifiers == entity.modifiers:
                    return android_entity
            return -1

    for item in honor:
        if item.isHonor == -1:
            # start_index = item.id
            # end_index = start_index
            # is_honor = 0
            if find_same(item) != -1:
                item.set_honor(0)
                # temp = item
                # while True:
                #     if temp.parentId < 0:
                #         is_honor = 0 if find_same(temp) != -1 else 1
                #         end_index = temp.id
                #         break
                #     temp = honor[temp.parentId]
                #     if temp.isHonor != -1:
                #         is_honor = temp.isHonor
                #         end_index = temp.id
                #         break
                #     elif find_same(temp) == -1:
                #         is_honor = 1
                #         end_index = temp.id
                #         break
                # end_id = honor[end_index].parentId
                # while start_index != end_id:
                #     temp_entity = honor[start_index]
                #     temp_entity.set_honor(is_honor)
                #     start_index = temp_entity.parentId
                #     if is_honor == 0 and temp_entity.accessibility != '':
                #         temp_entity.set_access(access_map[android[find_same(temp_entity)].accessibility] + \
                #                                access_map[temp_entity.accessibility])
            else:
                item.set_honor(1)


def get_dependency_section(entitiesHonor, cellsHonor, entitiesAndroid, cellsAndroid, outPath):
    print('get relation diff set')
    # 生成实体和依赖集
    honors: List[Entity] = []
    androids: List[Entity] = []
    for item in entitiesHonor:
        if not item['external']:
            honors.append(Entity(**item))
    for item in entitiesAndroid:
        if not item['external']:
            androids.append(Entity(**item))

    # 生成依赖diff集
    get_honor_entities(honors, androids)
    relations_android = set()
    diff: List[Relation] = []

    def get_relation(source, rel_dict: dict):
        src_entity = source[rel_dict['src']].__str__()
        dest_entity = source[rel_dict['dest']].__str__()
        bind_entity = -1
        relation_type = ""
        for key in rel_dict['values']:
            if key == 'bindVar':
                bind_entity = rel_dict['values'][key]
            else:
                relation_type = key
        return src_entity, dest_entity, bind_entity, relation_type

    for item in cellsAndroid:
        src, dest, bind_var, relation = get_relation(androids, item)
        bind_var_entity = androids[bind_var].__str__() if bind_var != -1 else ""
        hash_rel = src + bind_var_entity + relation + dest
        relations_android.add(hash_rel)

    android_contain_set = []
    for item in cellsHonor:
        src, dest, bind_var, relation = get_relation(honors, item)
        bind_var_entity = honors[bind_var].__str__() if bind_var != -1 else ""
        hash_rel = src + bind_var_entity + relation + dest
        if honors[item['src']].isHonor == 0 and honors[item['dest']].isHonor == 0:
            # 切面中可能会使用AOSP中原生的Define依赖
            if relation == 'Define':
                android_contain_set.append(
                    Relation(src={"id": item['src'], "isHonor": 0}, bind_var=bind_var, rel=relation,
                             dest={"id": item['dest'], "isHonor": 0}))
            # relations_honor.add(src + '->' + dest)
            if hash_rel not in relations_android:
                diff.append(
                    Relation(src={"id": item['src'], "isHonor": honors[item['src']].isHonor}, bind_var=bind_var,
                             rel=relation, dest={"id": item['dest'], "isHonor": honors[item['dest']].isHonor}))
        else:
            diff.append(Relation(src={"id": item['src'], "isHonor": honors[item['src']].isHonor}, bind_var=bind_var,
                                 rel=relation, dest={"id": item['dest'], "isHonor": honors[item['dest']].isHonor}))

    # FileReader().write_to_json(outPath, section, 0)
    return honors, diff, android_contain_set


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--honor', '-c', action='store', dest='honor',
                        help='root json file of honor')
    parser.add_argument('--android', '-a', action='store', dest='android',
                        help='root json file of android')
    parser.add_argument('--output', '-o', action='store', dest='output',
                        help='root directory of out')
    args = parser.parse_args()
    dispatch(args)


def dispatch(args):
    if not hasattr(args, 'honor'):
        raise ValueError("root directory of project must supply")

    if args.honor is None:
        raise ValueError("root directory of project must supply")
    if args.android is None:
        raise ValueError("root directory of project must supply")
    if args.output is None:
        raise ValueError("root directory of project must supply")
    entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
        FileReader().read_from_json(args.android, args.honor)
    intrusive_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-17/base/blame/lineageos_mixed_entities.csv')
    assi_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-17/base/blame/lineageos_pure_third_party_entities.csv')
    commit_null_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-17/base/blame/lineageos_all_entities.csv')
    base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                            entities_stat_aosp, intrusive_entities, assi_entities, commit_null_entities)
    match_set_stat, match_set, union_temp, anti_patterns = AntiPattern(Match(base_model)).start_detect()

    # honors, diff, android_contain_set = get_dependency_section(entities_honor, cells_honor, entities_aosp, cells_aosp,
    #                                                            args.output)
    # match_set_stat, match_set, union_temp, anti_patterns = ModeMatch(base_model, entities_stat_honor,
    #                                                                  android_contain_set).matchMode()

    FileReader().write_match_mode(args.output, match_set)
    FileReader().write_to_json(args.output, union_temp, 1)
    FileReader().write_to_json(args.output, anti_patterns, 3)
    FileReader().write_to_json(args.output, match_set_stat, 4)


if __name__ == '__main__':
    main()

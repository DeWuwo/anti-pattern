import argparse
from functools import partial
from typing import List
from collections import defaultdict
from utils import FileReader
from model.entity import Entity
from model.relation import Relation
from model.mode import ModeMatch

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
                if android[android_entity].accessibility == entity.accessibility:
                    return android_entity
            return -1

    for item in honor:
        if item.isHonor == -1:
            start_index = item.id
            end_index = start_index
            is_honor = 0
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
    honors: List[Entity] = []
    androids: List[Entity] = []
    for item in entitiesHonor:
        if not item['external']:
            honors.append(Entity(**item))
    for item in entitiesAndroid:
        if not item['external']:
            androids.append(Entity(**item))

    get_honor_entities(honors, androids)
    relations_android = set()
    diff: List[Relation] = []
    for item in cellsAndroid:
        src = androids[item['src']].__str__()
        dest = androids[item['dest']].__str__()
        relation = ""
        for rel in item['values']:
            relation = rel
        relations_android.add(src + relation + dest)
    android_contain_set = []
    for item in cellsHonor:
        src = honors[item['src']].__str__()
        dest = honors[item['dest']].__str__()
        relation = ""
        for rel in item['values']:
            relation = rel

        if honors[item['src']].isHonor == 0 and honors[item['dest']].isHonor == 0:
            # 切面中可能会使用AOSP中原生的Contain依赖
            if relation == 'Contain':
                android_contain_set.append(
                    Relation(src={"id": item['src'], "isHonor": 0}, rel=relation,
                             dest={"id": item['dest'], "isHonor": 0}))
            # relations_honor.add(src + '->' + dest)
            if src + relation + dest not in relations_android:
                diff.append(
                    Relation(src={"id": item['src'], "isHonor": honors[item['src']].isHonor}, rel=relation,
                             dest={"id": item['dest'], "isHonor": honors[item['dest']].isHonor}))
        else:
            diff.append(Relation(src={"id": item['src'], "isHonor": honors[item['src']].isHonor}, rel=relation,
                                 dest={"id": item['dest'], "isHonor": honors[item['dest']].isHonor}))

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
    honors, diff, android_contain_set = get_dependency_section(entities_honor, cells_honor, entities_aosp, cells_aosp,
                                                               args.output)
    match_set_stat, match_set, union_temp, anti_patterns = ModeMatch(honors, entities_stat_honor, diff,
                                                                     android_contain_set).matchMode()

    FileReader().write_match_mode(args.output, match_set)
    FileReader().write_to_json(args.output, union_temp, 1)
    FileReader().write_to_json(args.output, anti_patterns, 3)
    FileReader().write_to_json(args.output, match_set_stat, 4)


if __name__ == '__main__':
    main()

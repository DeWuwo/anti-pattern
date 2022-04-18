from typing import List, Dict
from model.relation import Relation
from model.entity import Entity
from model.build_model import BuildModel


class Match:
    base_model: BuildModel
    match_result: List[Dict[str, List[List[Relation]]]]
    match_result_statistic: Dict[str, Dict[str, int]]

    def __init__(self, model: BuildModel):
        self.base_model = model
        self.match_result = []
        self.match_result_statistic = {}

    # 命令中实体属性解析
    def entity_rule(self, entity_stack: List[Relation], entity: dict):
        entity_category: str = entity['category']
        if entity['id'][0] == 'id':
            pre_edge = entity_stack[entity['id'][1]]
            if entity['id'][2] == 0:
                entity_base = pre_edge.src['id']
            else:
                entity_base = pre_edge.dest['id']
        elif entity['id'][0] == 'bindType':
            entity_base = entity_stack[entity['id'][1]].bind_var
        else:
            entity_base = entity_category
        entity_attrs: dict = entity['attrs']
        entity_attrs.update({'category': entity_category})
        return entity_base, entity_attrs

    def handle_attr_match(self, entity: Entity, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_{key}', None)
            if not method(entity, val):
                return False
        return True

    def handle_category(self, entity: Entity, category: str):
        return category == '' or entity.category == category

    def handle_accessible(self, entity: Entity, accessible: List[str]):
        return (not accessible) or entity.accessible in accessible

    def handle_hidden(self, entity: Entity, hidden: bool):
        return (not hidden) or entity.id in self.base_model.hidden_entities

    def handle_final(self, entity: Entity, final: bool):
        return (not final) or entity.id in self.base_model.final_modify_entities

    def handle_accessible_modify(self, entity: Entity, accessible_modify: bool):
        return (not accessible_modify) or entity.id in self.base_model.access_modify_entities

    def handle_intrusive(self, entity: Entity, intrusive: bool):
        return (not intrusive) or entity.is_intrusive

    # 匹配函数
    def handle_matching(self, result_set: list, example_stack: list, flag: list, graph, current):
        src = graph[current]['src']
        rel = graph[current]['rel']
        dest = graph[current]['dest']
        not_aosp = graph[current]['direction']
        src_base, src_attr = self.entity_rule(example_stack, src)
        dest_base, dest_attr = self.entity_rule(example_stack, dest)
        for item in self.base_model.query_relation(rel, not_aosp, src_base, dest_base):
            if self.handle_attr_match(self.base_model.entity_assi[item.src['id']], **src_attr) and \
                    self.handle_attr_match(self.base_model.entity_assi[item.dest['id']], **dest_attr) and \
                    str(item.src['id']) + str(item.dest['id']) not in flag:
                next_stack = example_stack[:]
                next_stack.append(item)
                flag_update = flag[:]
                flag_update.append(str(item.src['id']) + str(item.dest['id']))
                if current < len(graph) - 1:
                    current += 1
                    self.handle_matching(result_set, next_stack, flag_update, graph, current)
                    current -= 1
                else:
                    result_set.append(next_stack)

    def general_rule_matching(self, pattern: str, rules: list):
        """
        通用的模式匹配
        :return:
        """
        '''
        rules = [
            [{'id': [-1], 'category': 'Class', 'attr': {'accessible': []}}, 'Inherit',
             {'id': [-1], 'category': 'Class', 'attr': {'accessible': []}}, '10'],
            [{'id': ['id', 0, 0], 'category': 'Class', 'attr': {'accessible': []}}, 'Define',
             {'id': [-1], 'category': 'Method', 'attr': {'accessible': []}}, '11'],
            [{'id': ['id', 1, 1], 'category': 'Method', 'attr': {'accessible': []}}, 'Call',
             {'id': [-1], 'category': 'Method', 'attr': {'accessible': ['protected']}}, '10'],
            [{'id': ['id', 0, 1], 'category': 'Class', 'accessible': []}, 'Define',
             {'id': ['bindType', 2], 'category': 'Variable', 'attr': {'accessible': ['protected']}}, '00']
        ]
        '''
        print('start run Pattern: ', pattern)
        mode_set = []
        res = []
        for item in rules:
            self.handle_matching(mode_set, [], [], item, 0)
        res.extend(mode_set)
        self.match_result.append({pattern: res})

    def pre_del(self):
        self.match_result = []
        self.match_result_statistic = {}

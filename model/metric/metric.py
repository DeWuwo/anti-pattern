import os.path
from typing import List
from collections import defaultdict
from functools import partial

from model.dependency.relation import Relation
from model.dependency.entity import Entity, get_accessible_domain
from model.metric.metric_constant import MetricCons
from utils import FileCSV, Constant, FileCommon


class Metric:
    src_relation: defaultdict
    dest_relation: defaultdict
    mc_data: defaultdict
    query_relation: defaultdict
    entity_extensive: List[Entity]
    hidden_filter_list: List[str]
    sdk_apis: List[str]

    def __init__(self, relations: List[Relation], data_path: str, query_relation, entity_extensive: List[Entity],
                 hidden_filter_list: List[str], code_extension: str):
        self.src_relation = defaultdict(partial(defaultdict, list))
        self.dest_relation = defaultdict(partial(defaultdict, list))
        self.mc_data = defaultdict()
        for rel in relations:
            self.src_relation[rel.src][rel.rel].append(rel)
            self.dest_relation[rel.dest][rel.rel].append(rel)
        try:
            mc_data_list = FileCSV.read_dict_from_csv(os.path.join(data_path, 'mc/file-mc.csv'))
        except FileNotFoundError:
            mc_data_list = []
        for data in mc_data_list:
            self.mc_data[str(data['filename']).replace('\\', '/')] = data
        self.query_relation = query_relation
        self.entity_extensive = entity_extensive
        self.hidden_filter_list = hidden_filter_list
        # self.sdk_apis = FileCommon.read_from_file_by_line(os.path.join(code_extension, 'api/current.txt'))

    def handle_metrics(self, metrics: dict, rels: List[Relation], **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_metrics_{key}', None)
            method(metrics, rels, val)

    def handle_metrics_init(self, **kwargs):
        metrics = {}
        for key, val in kwargs.items():
            if key == MetricCons.Me_native_used_frequency or key == MetricCons.Me_extensive_used_frequency or \
                    key == MetricCons.Me_native_used_effectiveness:
                metrics[key] = {}
            elif key == MetricCons.Me_extensive_access_frequency or key == MetricCons.Me_native_access_frequency:
                metrics[key] = {}
                for access in Constant.accessible_list:
                    metrics[key][access] = 0
            elif key == MetricCons.Me_stability:
                metrics[key] = {}
            elif key == MetricCons.Me_module:
                metrics[key] = ''
            elif key == MetricCons.Me_acceptable_hidden:
                metrics[key] = []
            elif key == MetricCons.Me_add_param:
                metrics[key] = {}
                metrics[key]['count'] = 0
                metrics[key]['detail'] = []
            elif key == MetricCons.Me_inner_scale:
                metrics[key] = {}
                metrics[key]['inner_class_loc'] = 0
            elif key == MetricCons.Me_interface_number:
                metrics[key] = {}
                metrics[key]['total'] = 0
                metrics[key]['final'] = 0
                for access in Constant.accessible_list:
                    metrics[key][access] = 0
                metrics[key][Constant.E_variable] = 0
                metrics[key][Constant.E_method] = 0
                metrics[key][Constant.E_class] = 0
            elif key == MetricCons.Me_anonymous_class:
                metrics[key] = {}
        return metrics

    def handle_metrics_native_used_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        used_frequency = {}
        if self.entity_extensive[entity_id].category == Constant.E_method:
            res = self.query_relation[Constant.call]['10'][Constant.E_method][entity_id]
            used_frequency = {
                'used_by_extension': len(res),
                'used_by_native': self.entity_extensive[entity_id].called - len(res)
            }
        elif self.entity_extensive[entity_id].category == Constant.E_class:
            res = self.query_relation[Constant.typed]['10'][Constant.E_variable][entity_id]
            used_frequency = {
                'used_by_extension': len(res),
                'used_by_native': len(self.dest_relation[entity_id][Constant.typed]) - len(res)
            }
        metrics[MetricCons.Me_native_used_frequency] = used_frequency

    # 对于修改访问权限的有效访问
    def handle_metrics_native_used_effectiveness(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        current_entity = self.entity_extensive[entity_id]
        metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] = 0
        metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_saturatedly'] = 0
        source_domain = Constant.accessible_level[current_entity.intrusive_modify['access_modify'].split('-')[0]]
        target_domain = Constant.accessible_level[current_entity.intrusive_modify['access_modify'].split('-')[1]]
        for rel in self.query_relation[Constant.call]['10'][Constant.E_method][entity_id]:
            access_domain = get_accessible_domain(current_entity, self.entity_extensive[rel.src], self.entity_extensive)
            if access_domain == target_domain:
                metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_saturatedly'] += 1
            elif source_domain < access_domain < target_domain:
                metrics[MetricCons.Me_native_used_effectiveness]['used_by_extension_effectively'] += 1

    def handle_metrics_extensive_used_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        used_frequency = {}
        if self.entity_extensive[entity_id].category == Constant.E_method:
            res = self.query_relation[Constant.call]['01'][Constant.E_method][entity_id]
            used_frequency = {
                'used_by_extension': self.entity_extensive[entity_id].called - len(res),
                'used_by_native': len(res)
            }
        elif self.entity_extensive[entity_id].category == Constant.E_class:
            res = self.query_relation[Constant.R_import]['01'][Constant.E_file][entity_id]
            used_frequency = {
                'used_by_extension': len(self.dest_relation[entity_id][Constant.R_import]) - len(res),
                'used_by_native': len(res)
            }
        metrics[MetricCons.Me_extensive_used_frequency] = used_frequency

    def handle_metrics_extensive_access_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_extensive_access_frequency][self.entity_extensive[entity_id].accessible] += 1

    # 用于原生聚合扩展时，记录调用扩展的数量
    def handle_metrics_native_access_frequency(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_native_access_frequency][self.entity_extensive[entity_id].accessible] += 1

    def handle_metrics_func_metrics(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_module] = 'test' \
            if 'test' in self.entity_extensive[entity_id].qualifiedName else 'not test'

    def handle_metrics_stability(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_stability]['entity'] = self.entity_extensive[entity_id].qualifiedName
        metrics[MetricCons.Me_stability]['history_commits'] = self.entity_extensive[entity_id].commits_count
        try:
            metrics[MetricCons.Me_stability]['maintenance_cost'] = self.mc_data[
                self.entity_extensive[entity_id].file_path]
        except KeyError:
            pass

    def handle_metrics_is_inherit(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_inherit] = [self.entity_extensive[src_entity].qualifiedName for src_entity in
                                             self.query_relation[Constant.inherit]['10'][Constant.E_class][entity_id]]

    def handle_metrics_is_override(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_is_override] = [self.entity_extensive[src_entity].qualifiedName for src_entity in
                                              self.query_relation[Constant.override]['10'][Constant.E_method][
                                                  entity_id]]

    def handle_metrics_acceptable_hidden(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        for name in self.hidden_filter_list:
            if self.entity_extensive[entity_id].qualifiedName.startswith(name):
                metrics[MetricCons.Me_acceptable_hidden].append(True)
                break
        metrics[MetricCons.Me_acceptable_hidden].append(False)

    def handle_metrics_unacceptable_non_hidden(self, metrics: dict, rels: List[Relation], target_entity: list):
        pass

    def handle_metrics_inner_scale(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if not metrics[MetricCons.Me_inner_scale]['inner_class_loc']:
            metrics[MetricCons.Me_inner_scale]['inner_class_loc'] = \
                self.entity_extensive[entity_id].end_line - self.entity_extensive[entity_id].start_line

            parent_outer_class = self.entity_extensive[self.entity_extensive[entity_id].parentId]
            metrics[MetricCons.Me_inner_scale]['outer_class_loc'] = \
                parent_outer_class.end_line - parent_outer_class.start_line

    def handle_metrics_interface_number(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if not metrics[MetricCons.Me_interface_number]['total']:
            metrics[MetricCons.Me_interface_number]['total'] = len(self.src_relation[entity_id][Constant.define])
            for rel in self.src_relation[entity_id][Constant.define]:
                dest_entity = self.entity_extensive[rel.dest]
                metrics[MetricCons.Me_interface_number][dest_entity.category] += 1
                metrics[MetricCons.Me_interface_number][dest_entity.accessible] += 1
                if dest_entity.final:
                    metrics[MetricCons.Me_interface_number]['final'] += 1

    def handle_metrics_add_param(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        metrics[MetricCons.Me_add_param]['count'] += 1
        temp_info = {'param_name': self.entity_extensive[entity_id].name,
                     'param_type': self.entity_extensive[entity_id].raw_type,
                     'used_times': len(self.dest_relation[entity_id][Constant.use])
                     }
        metrics[MetricCons.Me_add_param]['detail'].append(temp_info)

    def handle_metrics_anonymous_class(self, metrics: dict, rels: List[Relation], target_entity: list):
        entity_id = rels[target_entity[0]].dest if target_entity[1] else rels[target_entity[1]].src
        if not metrics[MetricCons.Me_anonymous_class]:
            metrics[MetricCons.Me_anonymous_class] = {
                'is_anonymous_class': self.entity_extensive[entity_id].is_anonymous_class
            }

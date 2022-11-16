import threading
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from model.relation import Relation
from model.entity import Entity
from model.build_model import BuildModel
from model.patterns.pattern_type import PatternType
from utils import FileJson, FileCSV, Constant
from model.blame_field import BlameField
from model.patterns.pattern_rules import PatternRules, RelationRule
from script.code_count import CodeInfo


class Match:
    base_model: BuildModel
    output: str
    out_path: str
    match_result: List[Dict[str, Dict[str, Dict[str, Dict[str, List[dict]]]]]]
    match_result_union: List[Dict[str, Dict[str, Dict[str, Dict[str, List[dict]]]]]]
    match_result_base_statistic: Dict[str, Dict[str, int]]
    # 不同粒度数量统计
    statistic_pkgs: Dict[str, Dict[str, int]]
    statistic_files: Dict[str, Dict[str, int]]
    statistic_entities: Dict[int, Dict[str, int]]
    statistic_modules: Dict[str, Dict[str, int]]
    module_blame: defaultdict

    def __init__(self, build_model: BuildModel, output: str, blame_path: str):
        self.base_model = build_model
        self.output = output
        self.out_path = output
        self.match_result = []
        self.match_result_union = []
        self.match_result_base_statistic = {}
        self.statistic_files = {}
        self.statistic_pkgs = {}
        self.statistic_entities = {}
        self.statistic_modules = {}
        self.module_blame = BlameField(blame_path).read_blame_field()

    # 命令中实体属性解析
    def entity_rule(self, entity_stack: List[Relation], entity: dict):
        entity_category: str = entity['category']
        if entity['id'][0] == 'id':
            pre_edge = entity_stack[entity['id'][1]]
            if entity['id'][2] == 0:
                entity_base = pre_edge.src
            else:
                entity_base = pre_edge.dest
        elif entity['id'][0] == 'bindVar':
            entity_base = entity_stack[entity['id'][1]].bind_var
        else:
            entity_base = entity_category
        entity_attrs: dict = entity['attrs']
        entity_attrs.update({'category': entity_category})
        try:
            entity_filter: dict = entity['filter']
        except:
            entity_filter = {}
        return entity_base, entity_attrs, entity_filter

    def handle_entity_attr_match(self, entity: Entity, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_{key}', None)
            if not method(entity, val):
                return False
        return True

    def handle_category(self, entity: Entity, category: str):
        return category == '' or entity.category == category

    def handle_accessible(self, entity: Entity, accessible: List[str]):
        return (not accessible) or entity.accessible in accessible

    def handle_intrusive(self, entity: Entity, intrusive: bool):
        return not intrusive ^ (entity.is_intrusive == 1)

    def handle_hidden(self, entity: Entity, hidden: List[str]):
        if Constant.hidden_map(entity.hidden) in hidden:
            return True
        return False

    def handle_final(self, entity: Entity, final: bool):
        return not final ^ (entity.id in self.base_model.final_modify_entities)

    def handle_accessible_modify(self, entity: Entity, accessible_modify: bool):
        return not accessible_modify ^ (entity.id in self.base_model.access_modify_entities)

    def handle_hidden_modify(self, entity: Entity, hidden_modify: bool):
        return not hidden_modify ^ (entity.id in self.base_model.hidden_modify_entities)

    def handle_obsolete(self, entity: Entity, obsolete: bool):
        return not obsolete ^ (entity.old_aosp >= 1)

    def handle_qualified_name(self, entity: Entity, qualified_name: List[str]):
        for name in qualified_name:
            if entity.qualifiedName.startswith(name):
                return True
        return False

    # 实体属性过滤
    def handle_entity_filter(self, entity: Entity, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_{key}', None)
            if method(entity, val):
                return True
        return False

    # 依赖属性匹配
    def handle_relation_attr_match(self, relation: Relation, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_{key}', None)
            if not method(relation, val):
                return False
        return True

    def handle_set_accessible(self, relation: Relation, set_accessible: bool):
        return not set_accessible ^ (relation.setAccessible == 1)

    def handle_invoke(self, relation: Relation, invoke: bool):
        return not invoke ^ (relation.invoke == 1)

    # metrics init
    def handle_metrics_init(self, **kwargs):
        metrics = {}
        for key, val in kwargs.items():
            if key == Constant.Me_called:
                metrics[key] = {}
            elif key == Constant.Me_access:
                metrics[key] = {}
                for access in Constant.accessible_list:
                    metrics[key][access] = 0
            elif key == Constant.Me_static:
                metrics[key] = {}
            elif key == Constant.Me_module:
                metrics[key] = ''
        return metrics

    #
    def handle_metrics(self, metrics: dict, rels: List[Relation], **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_metrics_{key}', None)
            method(metrics, rels, val)

    def handle_metrics_called_times(self, metrics: dict, rels: List[Relation], point: list):
        entity_id = rels[point[0]].dest if point[1] else rels[point[1]].src
        res = self.base_model.query_relation(Constant.call, '10', Constant.E_method,entity_id)
        called_times = {
            'called_by_extension': len(res),
            'called_by_native': self.base_model.entity_extensive[entity_id].called - len(res)
        }
        metrics[Constant.Me_called] = called_times

    def handle_metrics_access_metrics(self, metrics: dict, rels: List[Relation], point: list):
        entity_id = rels[point[0]].dest if point[1] else rels[point[1]].src
        metrics[Constant.Me_access][self.base_model.entity_extensive[entity_id].accessible] += 1

    def handle_metrics_func_metrics(self, metrics: dict, rels: List[Relation], point: list):
        entity_id = rels[point[0]].dest if point[1] else rels[point[1]].src
        metrics[Constant.Me_module] = 'test' \
            if 'test' in self.base_model.entity_extensive[entity_id].qualifiedName \
            else 'not test'

    def handle_metrics_static_metrics(self, metrics: dict, rels: List[Relation], point: list):
        entity_id = rels[point[0]].dest if point[1] else rels[point[1]].src
        metrics[Constant.Me_static] = self.base_model.entity_extensive[entity_id].commits_count

    # 匹配函数
    def handle_matching(self, result_set: list, filter_set: list, example_stack: list, flag: list, filter_cond: list,
                        rules: List[RelationRule], current):
        src = rules[current].src
        rel = rules[current].rel['type']
        dest = rules[current].dest
        not_aosp = rules[current].direction
        src_base, src_attr, src_filter = self.entity_rule(example_stack, src)
        dest_base, dest_attr, dest_filter = self.entity_rule(example_stack, dest)
        rel_attr = rules[current].rel['attrs']
        if len(rules) == 1:
            flag_map = defaultdict(list)
            filter_map = defaultdict(list)
            for item in self.base_model.query_relation(rel, not_aosp, src_base, dest_base):
                if self.handle_entity_attr_match(self.base_model.entity_extensive[item.src], **src_attr) and \
                        self.handle_entity_attr_match(self.base_model.entity_extensive[item.dest], **dest_attr) and \
                        self.handle_relation_attr_match(item, **rel_attr):
                    if self.handle_entity_filter(self.base_model.entity_extensive[item.src], **src_filter) or \
                            self.handle_entity_filter(self.base_model.entity_extensive[item.dest], **dest_filter):
                        filter_map[item.src].append(item)
                    else:
                        flag_map[item.src].append(item)
            for item in flag_map:
                result_set.append(flag_map[item])
            for item in filter_map:
                filter_set.append(filter_map[item])
        else:
            for item in self.base_model.query_relation(rel, not_aosp, src_base, dest_base):
                if self.handle_entity_attr_match(self.base_model.entity_extensive[item.src], **src_attr) and \
                        self.handle_entity_attr_match(self.base_model.entity_extensive[item.dest], **dest_attr) and \
                        self.handle_relation_attr_match(item, **rel_attr) and \
                        str(item.src) + str(item.dest) not in flag:
                    next_stack = example_stack[:]
                    next_stack.append(item)
                    flag_update = flag[:]
                    flag_update.append(str(item.src) + str(item.dest))
                    if self.handle_entity_filter(self.base_model.entity_extensive[item.src], **src_filter) or \
                            self.handle_entity_filter(self.base_model.entity_extensive[item.dest],
                                                      **dest_filter):
                        filter_cond[current] = True
                    else:
                        filter_cond[current] = False
                    if current < len(rules) - 1:
                        current += 1
                        self.handle_matching(result_set, filter_set, next_stack, flag_update, filter_cond, rules,
                                             current)
                        current -= 1
                    else:
                        if True in filter_cond:
                            filter_set.append(next_stack)
                        else:
                            result_set.append(next_stack)

    def general_rule_matching(self, rule: PatternRules):
        """
        通用的模式匹配
        :return:
        """
        print('      detect Pattern: ', rule.name)
        # res = []
        res = {}
        res_union = {}
        for style in rule.styles:
            mode_set = []
            filter_set = []
            self.handle_matching(mode_set, filter_set, [], [], [False, False, False, False, False], style.rules, 0)
            res[style.name] = {'res': mode_set, 'filter': filter_set}
            res_union[style.name] = {
                'res': self.aggregate_res_and_get_metrics(mode_set, rule.union_point, rule.union_edge, style.metrics),
                'filter': self.aggregate_res_and_get_metrics(filter_set, rule.union_point, rule.union_edge,
                                                             style.metrics)}

        self.match_result.append({rule.name: res})
        self.match_result_union.append({rule.name: res_union})

    def pre_del(self):
        self.match_result = []
        self.match_result_union = []
        self.match_result_base_statistic = {}
        self.statistic_files = {}
        self.statistic_pkgs = {}
        self.statistic_entities = {}
        self.statistic_modules = {}

    # 统计
    def get_root_file(self, entity_id: int) -> Entity:
        temp = self.base_model.entity_extensive[entity_id]
        while temp.category != 'File':
            temp = self.base_model.entity_extensive[temp.parentId]
        return temp

    # 模块统计
    def get_module_blame(self, entity_id: int) -> str:
        temp = self.base_model.entity_extensive[entity_id]
        blame_path = os.path.join(temp.bin_path, temp.file_path)
        blame_path.replace('\\', '/')
        for content in self.module_blame:
            if content in blame_path:
                return self.module_blame[content]
        return 'unknown_module'

    #
    def aggregate_res_and_get_metrics(self, res: List[List[Relation]], points, edges, metrics: dict):
        final_res = []
        index = 0
        count = len(res)

        def get_condition(rels: List[Relation], points_id: List):
            points_id_list = []
            for rel in range(0, len(points_id)):
                edge_id = rel // 2
                direction = rel % 2
                if points_id[rel]:
                    eid = rels[edge_id].dest if direction else rels[edge_id].src
                    points_id_list.append(eid)
                else:
                    points_id_list.append(-1)
            return points_id_list

        while index < count - 1:
            temp = res[index].copy()
            metrics_values = self.handle_metrics_init(**metrics)
            self.handle_metrics(metrics_values, res[index], **metrics)
            condition = get_condition(temp, points)
            for exa in range(index + 1, count):
                cond = get_condition(res[exa], points)
                if cond == condition:
                    self.handle_metrics(metrics_values, res[exa], **metrics)
                    for edge in edges:
                        temp.append(res[exa][edge])
                else:
                    final_res.append({'metrics': metrics_values, 'value': temp})
                    index = exa
                    break
                if exa == count - 1:
                    final_res.append({'metrics': metrics_values, 'value': temp})
                    index = exa
                    break

        return final_res

    def get_statistics(self, res_of_detect):
        print('get statistics')
        simple_stat = {}
        self.match_result_base_statistic['Total'] = {'files_count': self.base_model.statistics_extensive['File']}
        for item in res_of_detect:
            for pattern in item:
                self.match_result_base_statistic[pattern] = {}
                pattern_files_set = defaultdict(int)
                pattern_entities_set = defaultdict(int)
                pattern_module_set = defaultdict(int)
                pattern_pkgs_set = defaultdict(int)
                pattern_res: List[List[Relation]] = []
                for style_name, style_res in item[pattern].items():
                    for exa in style_res['res']:
                        pattern_res.append(exa['value'])
                    for exa in style_res['filter']:
                        pattern_res.append(exa['value'])
                simple_stat[pattern] = len(pattern_res)
                for exa in pattern_res:
                    temp_file_set = set()
                    temp_entity_set = set()
                    temp_module_set = set()
                    temp_pkg_set = set()
                    for rel in exa:
                        temp_entity_set.add(rel.src)
                        temp_entity_set.add(rel.dest)
                        src_file = self.get_root_file(rel.src).file_path
                        dest_file = self.get_root_file(rel.dest).file_path
                        temp_file_set.add(src_file)
                        temp_file_set.add(dest_file)
                        temp_module_set.add(self.get_module_blame(rel.src))
                        temp_module_set.add(self.get_module_blame(rel.dest))
                        temp_pkg_set.add(self.base_model.entity_extensive[rel.src].package_name)
                        temp_pkg_set.add(self.base_model.entity_extensive[rel.dest].package_name)

                    for file_name in temp_file_set:
                        pattern_files_set[file_name] += 1
                    for entity_id in temp_entity_set:
                        pattern_entities_set[entity_id] += 1
                    for module_blame in temp_module_set:
                        pattern_module_set[module_blame] += 1
                    for pkg in temp_pkg_set:
                        pattern_pkgs_set[pkg] += 1
                self.match_result_base_statistic[pattern] = {'example_count': len(item[pattern]),
                                                             'entities_count': len(pattern_entities_set),
                                                             'entities': pattern_entities_set,
                                                             'files_count': len(pattern_files_set),
                                                             'files': pattern_files_set}
                for file_name in pattern_files_set:
                    try:
                        self.statistic_files[file_name][pattern] = pattern_files_set[file_name]
                    except KeyError:
                        self.statistic_files[file_name] = {'filename': file_name}
                        self.statistic_files[file_name][pattern] = pattern_files_set[file_name]
                for entity_id in pattern_entities_set:
                    try:
                        self.statistic_entities[entity_id][pattern] = pattern_entities_set[entity_id]
                    except KeyError:
                        self.statistic_entities[entity_id] = self.base_model.entity_extensive[entity_id].to_csv()
                        self.statistic_entities[entity_id][pattern] = pattern_entities_set[entity_id]
                for module_blame in pattern_module_set:
                    try:
                        self.statistic_modules[module_blame][pattern] = pattern_module_set[module_blame]
                    except KeyError:
                        self.statistic_modules[module_blame] = {'module_blame': module_blame}
                        self.statistic_modules[module_blame][pattern] = pattern_module_set[module_blame]
                for pkg in pattern_pkgs_set:
                    try:
                        self.statistic_pkgs[pkg][pattern] = pattern_pkgs_set[pkg]
                    except KeyError:
                        self.statistic_pkgs[pkg] = {'packagename': pkg}
                        self.statistic_pkgs[pkg][pattern] = pattern_pkgs_set[pkg]
        return simple_stat

    def deal_res_for_output(self, filter_list: List[str], res_of_detect):
        print('ready for write')
        match_set = []
        union_temp_relation: List = []
        union_temp_entities = set()
        re_map = defaultdict(int)
        res = {}
        total_count = 0
        res['modeCount'] = len(res_of_detect)
        res['totalCount'] = total_count
        res['values'] = {}
        res_filter = {'modeCount': len(res_of_detect), 'values': {}}

        out_path = self.output
        # 'com.android.server.pm'
        if filter_list:
            out_path = os.path.join(out_path, filter_list[0])

        # 筛选输出希望实例
        def handle_filter(exa: List[Relation], filter_list: List[str]):
            if filter_list:
                for rel in exa:
                    if self.handle_qualified_name(self.base_model.entity_extensive[rel.src], filter_list) or \
                            self.handle_qualified_name(self.base_model.entity_extensive[rel.dest], filter_list):
                        return True
                return False
            return True

        for item in res_of_detect:
            for mode, mode_res in item.items():
                anti_temp = {}
                anti_temp_filter = {}
                pattern_count = 0
                pattern_count_filter = 0
                for style_name, style in mode_res.items():
                    style_res = {}
                    res_temp = []
                    filter_temp = []
                    for exa in style['res']:
                        if handle_filter(exa['value'], filter_list):
                            res_temp.append({'metrics': exa['metrics'], 'values': self.show_details(exa['value'])})
                            for rel in exa['value']:
                                s2d = str(rel.src) + '-' + str(rel.dest)
                                union_temp_entities.add(rel.src)
                                union_temp_entities.add(rel.dest)
                                if re_map[s2d] == 0:
                                    re_map[s2d] = 1
                                    union_temp_relation.append(self.to_detail_json(rel))

                    for exa in style['filter']:
                        if handle_filter(exa['value'], filter_list):
                            res_temp.append({'metrics': exa['metrics'], 'values': self.show_details(exa['value'])})
                            for rel in exa['value']:
                                s2d = str(rel.src) + '-' + str(rel.dest)
                                union_temp_entities.add(rel.src)
                                union_temp_entities.add(rel.dest)
                                if re_map[s2d] == 0:
                                    re_map[s2d] = 1
                                    union_temp_relation.append(self.to_detail_json(rel))
                    style_res['resCount'] = len(res_temp)
                    style_res['filterCount'] = len(filter_temp)
                    style_res['res'] = res_temp
                    style_res['filter'] = filter_temp
                    pattern_count += style_res['resCount']
                    pattern_count += style_res['filterCount']
                    pattern_count_filter += style_res['resCount']
                    anti_temp[style_name] = style_res
                    anti_temp_filter[style_name] = {'resCount': style_res['resCount'], 'res': style_res['res']}
                total_count += pattern_count
                match_set.append({mode: anti_temp})
                res['values'][mode] = {}
                res['values'][mode]['count'] = pattern_count
                res['values'][mode]['res'] = anti_temp
                res_filter['values'][mode] = {}
                res_filter['values'][mode]['count'] = pattern_count_filter
                res_filter['values'][mode]['res'] = anti_temp_filter
        res['totalCount'] = total_count
        return match_set, union_temp_relation, union_temp_entities, res, res_filter, out_path

    def to_detail_json(self, relation: Relation):
        return {"src": self.base_model.entity_extensive[relation.src].toJson(), "values": {relation.rel: 1},
                "dest": self.base_model.entity_extensive[relation.dest].toJson()}

    def show_details(self, section: List[Relation]):
        temp = []
        for index, item in enumerate(section):
            temp.append(self.to_detail_json(item))
        return temp

    def start_match_pattern(self, pattern: PatternType):
        print('start detect ', pattern.ident)
        threads = []
        self.pre_del()
        for rule in pattern.rules:
            th = threading.Thread(target=self.general_rule_matching(rule))
            threads.append(th)
        for th in threads:
            th.setDaemon(False)
            th.start()
        for th in threads:
            th.join()
        simple_stat = self.get_statistics(self.match_result_union)

        targets = [[], ['com.android.server.am'], ['com.android.server.pm'], ['com.android.systemui.statusbar'],
                   ['com.android.systemui.qs']]

        def output_to_file(file_list, res_of_detect):
            match_set, match_set_union_relation, match_set_union_entity, match_set_json_res, match_set_json_res_filter, out_path = \
                self.deal_res_for_output(file_list, res_of_detect)
            self.output_res(pattern.ident, match_set, match_set_union_relation, match_set_union_entity,
                            match_set_json_res,
                            match_set_json_res_filter, out_path)
            self.output_statistic(pattern.ident, pattern.patterns, simple_stat, out_path)

        for target in targets:
            output_to_file(target, self.match_result_union)
        self.output_module_res(pattern.ident)

    def output_res(self, pattern_type: str, match_set, match_set_union_relation, match_set_union_entity,
                   match_set_json_res, match_set_json_res_filter, out_path):
        output_path = os.path.join(out_path, pattern_type)
        print(f'output {pattern_type} match res')
        # FileJson.write_match_mode(output_path, match_set)
        FileJson.write_to_json(output_path, match_set_union_relation, 1)
        FileJson.write_to_json(output_path, match_set_json_res, 3)
        FileJson.write_to_json(output_path, match_set_json_res_filter, 6)
        FileCSV.write_entity_to_csv(output_path, 'coupling_entities',
                                    [self.base_model.entity_extensive[entity_id] for entity_id in
                                     match_set_union_entity],
                                    'facade')
        FileCSV.write_dict_to_csv(output_path, 'coupling_statistic', [
            {'coupling_relation': len(match_set_union_relation),
             'total_relation': len(self.base_model.relation_extensive),
             'coupling_entity': len(match_set_union_entity), 'total_entity': len(self.base_model.entity_extensive)}],
                                  'w')

    def output_statistic(self, pattern_type: str, patterns: List[str], simple_stat, out_path):
        output_path = os.path.join(out_path, pattern_type)

        # 输出检测结果
        FileJson.write_to_json(output_path, self.match_result_base_statistic, 4)
        # FileCSV.write_stat_to_csv('D:\\Honor\\match_res', pattern_type, datetime.now(), self.output.rsplit('\\', 4)[1],
        #                           self.output.rsplit('\\', 4)[2],
        #                           self.output.rsplit('\\', 4)[3], simple_stat)
        # 输出实体粒度统计
        headers = Entity.get_csv_header()
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'entity-pattern', headers, self.statistic_entities)
        # 输出文件粒度统计
        headers = ['filename']
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'file-pattern', headers, self.statistic_files)
        # 输出文件粒度统计
        headers = ['packagename']
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'package-pattern', headers, self.statistic_pkgs)

        # 输出模块粒度统计
        headers = ['module_blame']
        headers.extend(patterns)
        FileCSV.write_to_csv(output_path, 'module-pattern', headers, self.statistic_modules)

        # # 输出维护成本
        # try:
        #     left = os.path.join(self.output, Constant.file_mc)
        #     right = os.path.join(output_path, 'file-pattern.csv')
        #     FileCSV.merge_csv(left, right, ['filename'], self.output, pattern_type)
        # except FileNotFoundError as e:
        #     print(e)

    def output_module_res(self, pattern_type: str):
        print('     output special pkg info')
        targets = [{'pkg': '', 'path': ''},
                   {'pkg': 'com.android.server.am', 'path': 'services/core/java/com/android/server/am'},
                   {'pkg': 'com.android.server.pm', 'path': 'services/core/java/com/android/server/pm'},
                   {'pkg': 'com.android.systemui.statusbar',
                    'path': 'packages/SystemUI/src/com/android/systemui/statusbar'},
                   {'pkg': 'com.android.systemui.qs', 'path': 'packages/SystemUI/src/com/android/systemui/qs'}]
        res = []
        res2 = []
        res3 = []
        res4 = []
        for target in targets:
            code_info_count, code_info_count_sum = CodeInfo(self.out_path, pattern_type,
                                                            self.base_model.git_history.repo_path_accompany,
                                                            target).run()
            res.append(code_info_count)
            res2.append(code_info_count_sum)

            project = {'project': self.out_path.rsplit('\\')[-1]}
            temp = project.copy()
            temp2 = project.copy()
            temp.update(code_info_count)
            temp2.update(code_info_count_sum)
            res3.append(temp)
            res4.append(temp2)
        out_path = os.path.join(self.out_path, pattern_type)
        FileCSV.write_dict_to_csv(out_path, 'info_count', res, 'w')
        FileCSV.write_dict_to_csv(out_path, 'info_count_sum', res2, 'w')

        out_path = os.path.join('D:\\Honor\\match_res', pattern_type)
        FileCSV.write_dict_to_csv(out_path, 'info_count', res3, 'a')
        FileCSV.write_dict_to_csv(out_path, 'info_count_sum', res4, 'a')

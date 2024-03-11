import json
import os.path
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.dependency.entity import Entity, set_package, set_parameters
from model.dependency.relation import Relation
from model.dependency.graph import Graph
from model.generate_history import GenerateHistory
from model.blamer.entity_tracer import BaseState
from utils import FileCSV, FileJson, Compare, StringUtils, Hash, FileCommon
from constant.constant import Constant
from time import time
from model.differ.mapping import Mapping

MoveMethodRefactorings = {
    "Move And Rename Method": ["rename", "move"],
    "Move Method": ["move"],
    "Rename Method": ["rename"],
}

ExtractMethodRefactorings = {
    "Extract Method": ["extract"],
    "Extract And Move Method": ["extract", "move"]
}

MoveMethodParamRefactorings = {
    "Rename Parameter": ["param_modify"],
    "Add Parameter": ["param_modify"],
    "Remove Parameter": ["param_modify"],
}

MoveClassRefactoring = {
    "Rename Class": ["rename"],
    "Move Class": ["move"],
    "Move And Rename Class": ["rename", "move"]
}

all_refactor_type = MoveClassRefactoring.copy()
all_refactor_type.update(MoveMethodRefactorings)
all_refactor_type.update(MoveMethodParamRefactorings)
all_refactor_type.update(ExtractMethodRefactorings)


class BuildModel:
    # blame data
    generate_history: GenerateHistory
    # base info
    entity_android: List[Entity]
    entity_extensive: List[Entity]
    relation_android: List[Relation]
    relation_extensive: List[Relation]
    statistics_android: Dict
    statistics_extensive: Dict
    file_set_android: set
    file_set_extension: set

    out_path: str
    # more info
    hidden_entities: List[int]
    params_modify_entities: List[int]
    hidden_modify_entities: List[int]
    access_modify_entities: List[int]
    final_modify_entities: List[int]
    annotation_modify_entities: List[int]
    return_type_modify_entities: List[int]

    parent_class_modify_entities: List[int]
    parent_interface_modify_entities: List[int]

    class_body_modify_entities: List[int]
    inner_extensive_class_entities: List[int]
    class_var_extensive_entities: List[int]
    class_var_modify_entities: List[int]

    method_extensive_entities: List[int]
    method_body_modify_entities: List[int]
    method_var_extensive_entities: List[int]
    method_var_modify_entities: List[int]

    import_extensive_relation: List[Relation]

    refactor_entities: Dict[str, List[int]]
    agg_relations: List[Relation]
    facade_relations: List[Relation]
    facade_relations_error: List[Relation]
    facade_entities: List[Entity]
    facade_relations_on_file: Dict[str, Dict[str, list]]
    diff_relations: List[Relation]
    define_relations: List[Relation]
    reflect_relation: List[Relation]
    # query set
    query_map: defaultdict

    owner_proc: List[Dict]
    owner_proc_count: dict
    aosp_entity_set: defaultdict
    extensive_entity_set: defaultdict
    aosp_entity_set_um: dict
    extensive_entity_set_um: dict

    def __init__(self, entities_extensive, cells_extensive, statistics_extensive: Dict, entities_android, cells_android,
                 statistics_android: Dict, generate_history: GenerateHistory, out_path: str):
        # first init
        self.generate_history = generate_history
        self.out_path = out_path
        self.entity_android = []
        self.entity_extensive = []
        self.relation_android = []
        self.relation_extensive = []
        self.statistics_android = statistics_android
        self.statistics_extensive = statistics_extensive
        self.file_set_android = set()
        self.file_set_extension = set()
        # self.hidden_entities = []
        self.params_modify_entities = []
        self.hidden_modify_entities = []
        self.access_modify_entities = []
        self.final_modify_entities = []
        self.modifier_modify_entities = []
        self.annotation_modify_entities: List[int] = []
        self.return_type_modify_entities: List[int] = []
        self.type_modify_entities: List[int] = []

        self.parent_class_modify_entities: List[int] = []
        self.parent_interface_modify_entities: List[int] = []

        self.class_body_modify_entities = []
        self.inner_extensive_class_entities = []
        self.class_var_extensive_entities = []
        self.class_var_modify_entities = []

        self.method_extensive_entities = []
        self.method_body_modify_entities = []
        self.method_var_extensive_entities = []
        self.method_var_modify_entities = []
        self.import_extensive_relation = []
        self.refactor_entities = {
            "Move And Rename Method": [],
            "Move Method": [],
            "Rename Method": [],
            "Extract Method": [],
            "Extract And Move Method": [],
            "Rename Parameter": [],
            "Add Parameter": [],
            "Remove Parameter": [],
            "Rename Class": [],
            "Move Class": [],
            "Move And Rename Class": []
        }
        self.refactor_entities_new = {
            "rename": [],
            "extract": [],
            "move": [],
            "param_modify": [],
        }
        self.agg_relations = []
        self.facade_relations = []
        self.facade_relations_error = []
        self.facade_entities = []
        self.facade_relations_on_file = {}
        self.diff_relations = []
        self.define_relations = []
        self.reflect_relation = []
        self.owner_proc = []
        self.owner_proc_count = {}
        self.aosp_entity_set_um = {}
        self.extensive_entity_set_um = {}

        print("load conflict entity")
        conf_entities = {}
        conf_path = os.path.join(self.out_path, "conf_entities")
        if not os.path.exists(conf_path):
            os.mkdir(conf_path)
        for file in os.listdir(conf_path):
            res = FileJson.read_base_json(f"{conf_path}/{file}")

            for ent in res:
                ent_name = ent['qualifiedName']
                if ent_name not in conf_entities.keys():
                    conf_entities.update({ent_name: {'time': set(), 'blocks': 0, 'loc': 0}})
                conf_entities[ent_name]['time'].add(file)
                conf_entities[ent_name]['blocks'] += 1
                conf_entities[ent_name]['loc'] += ent['confLOC']

        # init entity
        print("start init model entities")
        self.aosp_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        self.extensive_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        # aosp entities
        print('     get aosp entities')
        for item in entities_android:
            if not item['external']:
                entity = Entity(**item)
                set_parameters(entity, self.entity_android)
                self.entity_android.append(entity)
                self.aosp_entity_set[entity.category][entity.qualifiedName][entity.file_path].append(entity.id)
                self.aosp_entity_set_um[entity.id] = entity
                if entity.category == Constant.E_file:
                    self.file_set_android.add(entity.file_path)
                elif entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                    entity.set_anonymous_class(True)
        # assi entities
        print('     get assi entities')
        for item in entities_extensive:
            if not item['external']:
                entity = Entity(**item)
                # get entity package
                set_package(entity, self.entity_extensive)
                set_parameters(entity, self.entity_extensive)
                self.entity_extensive.append(entity)
                self.extensive_entity_set[entity.category][entity.qualifiedName][entity.file_path].append(entity.id)
                self.extensive_entity_set_um[entity.id] = entity
                self.owner_proc.append(entity.to_csv())
                if entity.category == Constant.E_file:
                    self.file_set_extension.add(entity.file_path)
                elif entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                    entity.set_anonymous_class(True)
                if entity.qualifiedName in conf_entities.keys():
                    entity.set_conf_data(len(conf_entities['times']), conf_entities['blocks'], conf_entities['loc'])
        # init dep
        print("start init model deps")
        import_relation_set = defaultdict(int)
        print("     get aosp dep")
        for index, item in enumerate(cells_android):
            relation = Relation(**item)
            relation.set_id(index)
            relation.set_files(self.entity_android)
            self.relation_android.append(relation)
            if relation.rel == Constant.R_import:
                import_relation_set[relation.to_str(self.entity_android)] = 1
            elif relation.rel == Constant.typed:
                self.entity_android[relation.src].set_typed(relation.dest)
            elif relation.rel == Constant.R_annotate:
                self.entity_android[relation.dest].set_annotations(self.entity_android[relation.src].qualifiedName)
            elif relation.rel == Constant.inherit:
                self.entity_android[relation.src].set_parent_class(self.entity_android[relation.dest].qualifiedName)
            elif relation.rel == Constant.implement:
                self.entity_android[relation.src].set_parent_interface(self.entity_android[relation.dest].qualifiedName)
            elif relation.rel == Constant.param:
                self.entity_android[relation.src].set_param_entities(relation.dest)

        print("     get assi dep")
        temp_param = defaultdict(list)
        temp_define = defaultdict(list)
        for index, item in enumerate(cells_extensive):
            relation = Relation(**item)
            relation.set_id(index)
            relation.set_files(self.entity_extensive)
            self.relation_extensive.append(relation)
            if relation.rel == Constant.param:
                temp_param[relation.src].append(self.entity_extensive[relation.dest])
                self.entity_extensive[relation.dest].set_is_param(1)
                self.entity_extensive[relation.src].set_param_entities(relation.dest)
            elif relation.rel == Constant.define:
                temp_define[relation.src].append(self.entity_extensive[relation.dest])
                # 新增children属性
                self.entity_extensive[relation.src].set_children(relation.dest)
            elif relation.rel == Constant.R_import:
                if import_relation_set[relation.to_str(self.entity_extensive)] != 1 and \
                        self.entity_extensive[relation.src].file_path in self.file_set_android:
                    self.import_extensive_relation.append(relation)
            elif relation.rel == Constant.typed:
                self.entity_extensive[relation.src].set_typed(relation.dest)
            elif relation.rel == Constant.R_annotate:
                self.entity_extensive[relation.dest].set_annotations(self.entity_extensive[relation.src].qualifiedName)
            elif relation.rel == Constant.inherit:
                self.entity_extensive[relation.src].set_parent_class(self.entity_extensive[relation.dest].qualifiedName)
            elif relation.rel == Constant.implement:
                self.entity_extensive[relation.src].set_parent_interface(
                    self.entity_extensive[relation.dest].qualifiedName)
            elif relation.rel == Constant.call:
                self.entity_extensive[relation.dest].set_called_count(relation.src)
                self.entity_extensive[relation.src].set_call_count(relation.dest)

        # 生成依赖图
        # graph = Graph(self.entity_extensive, self.relation_extensive)
        # for ent in self.entity_extensive:
        #     graph.get_analysis(ent)

        # data get -- blame
        print('start init owner from blame')
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities, refactor_list = self.get_blame_data()

        #
        # for ent_id, ent in all_entities.items():
        #     self.entity_extensive[int(ent_id)].set_commits_count(
        #         {'actively_native': len(json.loads(ent['base commits'])),
        #          'obsolotely_native': len(json.loads(ent['old base commits'])),
        #          'extensive': len(json.loads(ent['accompany commits']))})

        # 计算部分实体hash
        self.cal_entity_hash()

        print('get ownership')
        # first get entity owner
        print('     get entity owner')
        self.get_entity_ownership(all_entities, all_native_entities,
                                  old_native_entities, old_update_entities, intrusive_entities,
                                  old_intrusive_entities, pure_accompany_entities, refactor_list,
                                  temp_define, temp_param)

        # Mapping(self.entity_android, self.entity_extensive, self.aosp_entity_set, self.extensive_entity_set,
        #         self.aosp_entity_set_um, self.extensive_entity_set_um).run_mapping_and_ownership(refactor_list,
        #                                                                                          self.generate_history.extensive_modify_files)

        print('     get relation owner')
        self.get_relation_ownership()

        print('get filter relation set')
        self.detect_facade()

        # query set build
        print('get relation search dictionary')
        self.query_map_build(self.diff_relations, self.define_relations)

        print('  output entities owner and intrusive info')
        self.out_intrusive_info()

        # output facade info
        self.out_facade_info()

    def get_complete_file_path(self, file_path, repo_extensive):
        if repo_extensive == 1:
            return os.path.join(self.generate_history.repo_path_accompany, file_path)
        else:
            return os.path.join(self.generate_history.repo_path_aosp, file_path)

    def cal_entity_hash_rule(self, entities: List[Entity], modify_files: set, hash_cache: list, is_ext: int):
        for entity in entities:
            # 只计算发生变更的文件
            if (not entity.above_file_level()) and entity.file_path in modify_files:
                if entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                    entity.set_total_hash(
                        Hash.get_hash_from_list(
                            FileCommon.read_file_to_scope(
                                self.get_complete_file_path(entity.file_path, is_ext),
                                entity.start_line, entity.start_column,
                                entity.end_line, entity.end_column
                            )
                        )
                    )
                if entity.category in [Constant.E_class, Constant.E_interface, Constant.E_annotation]:
                    entity.set_total_hash(
                        Hash.get_hash_from_list(
                            FileCommon.read_file_to_line(
                                self.get_complete_file_path(entity.file_path, is_ext),
                                entity.start_line, entity.end_line
                            )
                        )
                    )
                elif entity.category == Constant.E_method:
                    content = FileCommon.read_file_to_line(
                        self.get_complete_file_path(entity.file_path, is_ext),
                        entity.start_line, entity.end_line
                    )
                    hash_str = Hash.get_hash_from_list(content)
                    entity.set_total_hash(hash_str)
                    # body_content = FileCommon.read_file_to_line(
                    #     self.get_complete_file_path(entity.file_path, is_ext),
                    #     entity.body_start_line, entity.body_end_line
                    # )
                    # 暂时先处理成方法整体
                    body_content = FileCommon.read_file_to_line(
                        self.get_complete_file_path(entity.file_path, is_ext),
                        entity.start_line, entity.end_line
                    )
                    hash_str = Hash.get_hash_from_list(body_content)
                    entity.set_body_hash(hash_str)
                elif entity.category == Constant.E_variable:
                    entity.set_total_hash(
                        Hash.get_hash_from_list(
                            FileCommon.read_file_to_scope(
                                self.get_complete_file_path(entity.file_path, is_ext),
                                entity.start_line, entity.start_column,
                                entity.end_line, entity.end_column
                            )
                        )
                    )
                else:
                    content = FileCommon.read_file_to_line(
                        self.get_complete_file_path(entity.file_path, is_ext),
                        entity.start_line, entity.end_line
                    )
                    hash_str = Hash.get_hash_from_list(content)
                    entity.set_total_hash(hash_str)
                hash_cache.append(entity)

    def cal_entity_hash(self):
        start_time = time()
        if os.path.exists(f"{self.out_path}/aosp_hash.csv"):
            aosp_hash = FileCSV.read_dict_from_csv(f"{self.out_path}/aosp_hash.csv")
            for ent_hash in aosp_hash:
                self.entity_android[int(ent_hash['id'])].set_total_hash(ent_hash['total_hash'])
                if self.entity_android[int(ent_hash['id'])].category == Constant.E_method:
                    self.entity_android[int(ent_hash['id'])].set_total_hash(ent_hash['body_hash'])
        else:
            aosp_hash_cache = []
            print("cal aosp entity content hash")
            # 只计算发生变更的文件
            self.cal_entity_hash_rule(self.entity_android, self.generate_history.aosp_modify_files, aosp_hash_cache, 0)
            FileCSV.write_entity_to_csv(self.out_path, "aosp_hash", aosp_hash_cache, 'hash')
        if os.path.exists(f"{self.out_path}/extensive_hash.csv"):
            extensive_hash = FileCSV.read_dict_from_csv(f"{self.out_path}/extensive_hash.csv")
            for ent_hash in extensive_hash:
                self.entity_extensive[int(ent_hash['id'])].set_total_hash(ent_hash['total_hash'])
                if self.entity_extensive[int(ent_hash['id'])].category == Constant.E_method:
                    self.entity_extensive[int(ent_hash['id'])].set_total_hash(ent_hash['body_hash'])
        else:
            extensive_hash_cache = []
            print("cal extensive entity content hash")
            self.cal_entity_hash_rule(self.entity_extensive, self.generate_history.extensive_modify_files,
                                      extensive_hash_cache, 1)
            FileCSV.write_entity_to_csv(self.out_path, "extensive_hash", extensive_hash_cache, 'hash')
        end_time = time()
        print("load entity hash cost", end_time - start_time)

    # Get data of blame
    def get_blame_data(self):
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = self.generate_history.divide_owner()

        print('get possible refactor entity')
        possible_refactor_entities = {}
        possible_refactor_entities.update(intrusive_entities)
        possible_refactor_entities.update(old_intrusive_entities)
        possible_refactor_entities.update(pure_accompany_entities)
        refactor_list = self.generate_history.load_refactor_entity(possible_refactor_entities)
        return all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities, refactor_list

    # get owner string '01', '10', '11' or '00'
    def get_direction(self, relation: Relation):
        def get_owner(ent: Entity):
            # if ent.is_intrusive:
            #     return '0'
            # else:
            return str(ent.not_aosp)

        return get_owner(self.entity_extensive[relation.src]) + get_owner(self.entity_extensive[relation.dest])

    # Construction of query map
    def query_map_build(self, diff: List[Relation], android_define_set: List[Relation]):
        self.query_map = defaultdict(partial(defaultdict, partial(defaultdict, partial(defaultdict, list))))
        for item in diff:
            self.query_map[item.rel][self.get_direction(item)][self.entity_extensive[item.src].category][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][self.entity_extensive[item.src].category][
                item.dest].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel][self.get_direction(item)][item.src][item.dest].append(item)
        for item in android_define_set:
            self.query_map[item.rel]['00'][self.entity_extensive[item.src].category][
                self.entity_extensive[item.dest].category].append(item)

            self.query_map[item.rel]['00'][self.entity_extensive[item.src].category][item.dest].append(item)

            self.query_map[item.rel]['00'][item.src][self.entity_extensive[item.dest].category].append(item)
            self.query_map[item.rel]['00'][item.src][item.dest].append(item)

    # query method
    def query_relation(self, rel: str, not_aosp: str, src, dest) -> List[Relation]:
        return self.query_map[rel][not_aosp][src][dest]

    # diff & blame
    def get_entity_ownership(self, all_entities: dict, all_native_entities: dict,
                             old_native_entities: dict, old_update_entities: dict, intrusive_entities: dict,
                             old_intrusive_entities: dict, pure_accompany_entities: dict,
                             refactor_list: Dict[int, list],
                             child_define: Dict[int, List[Entity]], child_param: dict):
        keys_all_entities = all_entities.keys()
        keys_intrusive_entities = intrusive_entities.keys()
        keys_old_intrusive_entities = old_intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_old_native_entities = old_native_entities.keys()
        keys_old_update_entities = old_update_entities.keys()
        keys_all_native_entities = all_native_entities.keys()
        self.owner_proc_count = {
            'ignore': 0,
            'dep_coupling': 0,
            'dep_native': 0,
            'dep_extension': 0,
            'dep_any': 0,
            'git_pure_native': 0,
            'git_native': 0,
            'git_old_native': 0,
            'git_old_update': 0,
            'git_intrusive': 0,
            'git_old_intrusive': 0,
            'git_extension': 0,
            'git_any': 0,
            'refactor': 0,
            'dep_native2git_pure_native': 0,
            'dep_native2git_pure_native_c': [0, 0, 0, 0],
            'dep_native2git_native': 0,
            'dep_native2git_native_c': [0, 0, 0, 0],
            'dep_native2git_old_native': 0,
            'dep_native2git_old_native_c': [0, 0, 0, 0],
            'dep_native2git_old_update': 0,
            'dep_native2git_old_update_c': [0, 0, 0, 0],
            'dep_native2git_intrusive': 0,
            'dep_native2git_intrusive_c': [0, 0, 0, 0],
            'dep_native2git_old_intrusive': 0,
            'dep_native2git_old_intrusive_c': [0, 0, 0, 0],
            'dep_native2git_extension': 0,
            'dep_native2git_extension_c': [0, 0, 0, 0],
            'dep_extension2git_extension': 0,
            'dep_extension2git_extension_c': [0, 0, 0, 0],
            'dep_extension2git_native': 0,
            'dep_extension2git_native_c': [0, 0, 0, 0],
            'dep_extension2git_pure_native': 0,
            'dep_extension2git_pure_native_c': [0, 0, 0, 0],
            'dep_extension2git_old_native': 0,
            'dep_extension2git_old_native_c': [0, 0, 0, 0],
            'dep_extension2git_old_update': 0,
            'dep_extension2git_old_update_c': [0, 0, 0, 0],
            'dep_extension2git_intrusive': 0,
            'dep_extension2git_intrusive_c': [0, 0, 0, 0],
            'dep_extension2git_old_intrusive': 0,
            'dep_extension2git_old_intrusive_c': [0, 0, 0, 0],
            'parent_ref': 0,
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
            else:
                return 3

        def get_git_dep2git(ent: Entity):
            if ent.id in keys_old_native_entities:
                return '_0', "git_old_native"
            elif ent.id in keys_old_update_entities:
                return '_0 0', "git_old_update"
            elif ent.id in keys_intrusive_entities:
                return '0 1', "git_intrusive"
            elif ent.id in keys_old_intrusive_entities:
                return '_0 1', "git_old_intrusive"
            elif ent.id in keys_pure_accompany_entities:
                return '1', "git_extension"
            elif ent.id in keys_all_native_entities:
                return '0', "git_native"
            else:
                return '000', "git_pure_native"

        def detect_count(ent: Entity, dep_res):
            if dep_res == -1:
                dep_count = 'dep_extension'
                self.owner_proc[ent.id]['dep_diff'] = '1'
            else:
                dep_count = 'dep_native'
                self.owner_proc[ent.id]['dep_diff'] = '0'
            self.owner_proc_count[dep_count] += 1

            owner, owner_str = get_git_dep2git(ent)
            self.owner_proc[ent.id]['git_blame'] = owner
            self.owner_proc_count[owner_str] += 1

            if not ent.refactor:
                self.owner_proc_count[dep_count + '2' + owner_str] += 1
                self.owner_proc_count[dep_count + '2' + owner_str + '_c'][get_index(ent.category)] += 1

        def detect_ownership(ent: Entity, all_refactor_info: Dict[int, list], src_name: str, src_param: str,
                             src_file: str):
            if all_refactor_info is None:
                detect_un_refactor_entities(ent, src_name, src_param, src_file)
                return
            try:
                ent_refactor_info = all_refactor_info[ent.id][1]
                detect_refactor_entities(ent, ent_refactor_info, all_refactor_info)
            except KeyError:
                detect_un_refactor_entities(ent, src_name, src_param, src_file)

        def detect_git_must_native(ent: Entity):
            if ent.id not in keys_all_entities:
                return 1

        def detect_refactor_entities(ent: Entity, ent_refactor_info: list, all_refactor_info: Dict[int, list]):
            def detect_refactor_entities_son(child_entity_set: List[Entity], outer_ref_name: str, outer_ref_param: str,
                                             outer_ref_file_path: str):
                for child_ent in child_entity_set:
                    child_ent.set_refactor({'type': 'parent_ref'})
                    self.owner_proc[child_ent.id]['refactor'] = 'parent_ref'
                    child_source_qualified_name = outer_ref_name + '.' + child_ent.name
                    if child_ent.category == Constant.E_method:
                        child_source_param = child_ent.parameter_names
                    else:
                        child_source_param = outer_ref_param
                    detect_ownership(child_ent, all_refactor_info, child_source_qualified_name, child_source_param,
                                     outer_ref_file_path)
                    detect_refactor_entities_son(child_define[child_ent.id] + child_param[child_ent.id],
                                                 child_source_qualified_name, child_source_param, outer_ref_file_path)

            move_list = set()
            self.owner_proc_count['refactor'] += 1
            for move in ent_refactor_info:
                move_type: str = move[0]
                source_state: BaseState = move[1]
                dest_state: BaseState = move[2]
                # print(len(ent_refactor_info), ent.category, ent.id, move_type, source_state.longname(),
                #       dest_state.longname())

                # 对扩展重构
                dep_diff_res = self.graph_differ(ent, source_state.longname(), source_state.get_param(),
                                                 source_state.file_path)
                if dep_diff_res == -1 and ent.id in keys_pure_accompany_entities:
                    ent.set_honor(1)
                    self.owner_proc[ent.id]['dep_diff'] = '1'
                    self.owner_proc[ent.id]['git_blame'] = 'extension refactor'
                    continue
                ent.set_refactor(
                    {'type': move_type, 'source_name': source_state.longname(),
                     'source_param': source_state.get_param()})
                move_list.add(move_type)
                if move_type in MoveClassRefactoring.keys():
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in MoveMethodRefactorings.keys():
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in ExtractMethodRefactorings.keys():
                    ent.set_honor(1)
                    ent.set_intrusive(1)
                    for ent in child_param[ent.id]:
                        ent.set_honor(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param(), source_state.file_path)
                elif move_type in MoveMethodParamRefactorings.keys():
                    if ent.category == Constant.E_method:
                        ent.set_honor(0)
                        ent.set_intrusive(1)
                        detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id],
                                                     source_state.longname(),
                                                     source_state.get_param(), source_state.file_path)
                    else:
                        if move_type == "Rename Parameter":
                            ent.set_honor(0)
                            ent.set_intrusive(1)
                        elif move_type == "Add Parameter":
                            ent.set_honor(1)
                else:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    self.owner_proc[ent.id]['dep_diff'] = 'null'
                    self.owner_proc[ent.id]['git_blame'] = 'other refactor'

            self.owner_proc[ent.id]['refactor'] = ent.refactor
            for move in move_list:
                self.owner_proc_count[move] += 1
                self.refactor_entities[move].append(ent.id)
                for mv_type in all_refactor_type[move]:
                    self.refactor_entities_new[mv_type].append(ent.id)

        def detect_un_refactor_entities(ent: Entity, source_name: str, source_param: str, source_file: str):
            if ent.not_aosp != -2:
                self.owner_proc_count['parent_ref'] += 1
                return

            dep_diff_res = self.graph_differ(ent, source_name, source_param, source_file)
            detect_count(ent, dep_diff_res)
            if ent.id in keys_old_native_entities or ent.id in keys_old_update_entities:
                ent.set_honor(0)
                ent.set_old_aosp(1)
            elif ent.id in keys_old_intrusive_entities:
                ent.set_honor(0)
                ent.set_old_aosp(1)
                ent.set_intrusive(1)
            elif ent.id in keys_all_native_entities:
                ent.set_honor(0)
            elif ent.id in keys_intrusive_entities or ent.id in keys_pure_accompany_entities:
                if dep_diff_res > -1:
                    ent.set_honor(0)
                    if ent.is_param != 1:
                        ent.set_intrusive(1)
                else:
                    ent.set_honor(1)
            else:
                ent.set_honor(0 if dep_diff_res > -1 else 1)

        # start detect ownership
        for entity in self.entity_extensive:
            self.owner_proc[entity.id]['refactor'] = 'null'
            if entity.above_file_level():
                owner = 0 if self.graph_differ(entity, entity.qualifiedName, entity.parameter_names,
                                               entity.file_path) >= 0 else 1
                entity.set_honor(owner)
                self.owner_proc[entity.id]['dep_diff'] = 'ignore'
                self.owner_proc[entity.id]['git_blame'] = 'ignore'
                self.owner_proc_count['ignore'] += 1
            # 解耦仓实体
            elif entity.is_decoupling > 1:
                entity.set_honor(1)
                self.owner_proc[entity.id]['dep_diff'] = '1-coupling'
                self.owner_proc[entity.id]['git_blame'] = 'any'
                self.owner_proc_count['dep_coupling'] += 1
                self.owner_proc_count['git_any'] += 1
            elif StringUtils.find_str_in_short_list(entity.file_path, Constant.module_files):
                entity.set_honor(1)

            elif detect_git_must_native(entity):
                entity.set_honor(0)
                # if entity.category == constant.E_method and not entity.hidden:
                #     entity.set_hidden(['hidden'])
                self.graph_differ(entity, entity.qualifiedName, entity.parameter_names, entity.file_path)
                self.owner_proc[entity.id]['dep_diff'] = 'any'
                self.owner_proc[entity.id]['git_blame'] = '000'
                self.owner_proc_count['dep_any'] += 1
                self.owner_proc_count['git_pure_native'] += 1
            else:
                detect_ownership(entity, refactor_list, entity.qualifiedName, entity.parameter_names, entity.file_path)

    def struct_detect_ownership(self, all_entities: dict,
                                all_native_entities: dict,
                                old_native_entities: dict, old_update_entities: dict, intrusive_entities: dict,
                                old_intrusive_entities: dict, pure_accompany_entities: dict):
        # start detect ownership
        keys_all_entities = all_entities.keys()
        keys_intrusive_entities = intrusive_entities.keys()
        keys_old_intrusive_entities = old_intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_old_native_entities = old_native_entities.keys()
        keys_old_update_entities = old_update_entities.keys()
        keys_all_native_entities = all_native_entities.keys()

        mapping_failed_list: List[int] = []

        for ent in self.entity_extensive:
            if ent.above_file_level():
                owner = 0 if self.struct_info_mapping(ent) >= 0 else 1
                ent.set_honor(owner)
            # 解耦仓实体
            elif ent.is_decoupling > 1:
                ent.set_honor(1)
            elif StringUtils.find_str_in_short_list(ent.file_path, Constant.module_files):
                ent.set_honor(1)
            elif ent.id not in keys_all_entities:
                ent.set_honor(0)
                # if entity.category == constant.E_method and not entity.hidden:
                #     entity.set_hidden(['hidden'])
                owner = self.struct_info_mapping(ent)
                if owner < 0:
                    # todo: 可能发生外部重构
                    pass
            else:
                self.strict_mapping_entity_get_ownership(ent, mapping_failed_list)
        for ent in mapping_failed_list:
            # 粗略检测
            pass

    def struct_info_mapping(self, entity: Entity):
        aosp_list_full: List[int] = self.aosp_entity_set[entity.category][entity.qualifiedName][entity.file_path]
        extensive_list_full: List[int] = self.extensive_entity_set[entity.category][entity.qualifiedName][
            entity.file_path]

        aosp_list: List[int] = [ent for ent in aosp_list_full if self.entity_android[ent].entity_mapping == -1]
        extensive_list: List[int] = [ent for ent in extensive_list_full if
                                     self.entity_extensive[ent].entity_mapping == -1]
        aosp_list.sort()
        extensive_list.sort()

        if not aosp_list:
            return -1
        elif len(aosp_list) == len(extensive_list):
            for aosp_ent, extensive_ent in zip(aosp_list, extensive_list):
                self.get_entity_map(self.entity_android[aosp_ent], self.entity_extensive[extensive_ent])
            return entity.entity_mapping
        else:
            """
            /* 基础结构信息匹配，基于实体类型划分匹配规则，主要是方法的匹配
            """
            if entity.category == Constant.E_class and entity.anonymous != -1:
                for item_id in aosp_list:
                    if self.entity_android[item_id].raw_type == entity.raw_type and \
                            self.entity_android[self.entity_android[item_id].anonymous].name == \
                            self.entity_extensive[entity.anonymous].name:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_class or entity.category == Constant.E_interface:
                for item_id in aosp_list:
                    if self.entity_android[item_id].abstract == entity.abstract:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif Constant.anonymous_class in entity.qualifiedName:
                map_parent_anonymous_class = get_parent_anonymous_class(entity.id, self.entity_extensive).id
                for item_id in aosp_list:
                    aosp_parent_anonymous_class = get_parent_anonymous_class(item_id,
                                                                             self.entity_android).entity_mapping
                    if aosp_parent_anonymous_class == map_parent_anonymous_class:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_method or entity.category == Constant.E_variable:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_names == entity.parameter_names and \
                            (not (entity.not_aosp == 0 and entity.is_intrusive == 0) or
                             (self.entity_android[item_id].parameter_types == entity.parameter_types)):
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            else:
                return aosp_list[0]
            return -1

    def strict_mapping_entity_get_ownership(self, ent: Entity, mapping_failed_list: List[int]):
        owner = self.struct_info_mapping(ent)
        if owner > -1:
            # 基于历史信息获取归属方
            pass
        else:
            mapping_failed_list.append(ent.id)

    def rough_mapping_entity_get_ownership(self, ent: Entity, mapping_failed_list: List[int]):
        pass

    def load_entity_ownership_from_catch(self):
        owners = FileCSV.read_from_file_csv(os.path.join(self.out_path, 'final_ownership.csv'), True)
        for owner in owners:
            self.entity_extensive[int(owner[0])].set_honor(int(owner[1]))
            self.entity_extensive[int(owner[0])].set_old_aosp(int(owner[2]))
            self.entity_extensive[int(owner[0])].set_intrusive(int(owner[3]))
            if int(owner[3]) == 1:
                self.entity_extensive[int(owner[0])].set_entity_mapping(int(owner[7]))
                self.get_entity_map(self.entity_extensive[int(owner[0])], self.entity_android[int(owner[7])])

    # graph differ
    def graph_differ(self, entity: Entity, search_name: str, search_param: str, search_file: str):
        aosp_list_full: List[int] = self.aosp_entity_set[entity.category][search_name][search_file]
        extensive_list_full: List[int] = self.extensive_entity_set[entity.category][entity.qualifiedName][
            entity.file_path]

        aosp_list: List[int] = [ent for ent in aosp_list_full if self.entity_android[ent].entity_mapping == -1]
        extensive_list: List[int] = [ent for ent in extensive_list_full if
                                     self.entity_extensive[ent].entity_mapping == -1]

        if not aosp_list:
            return -1
        elif len(aosp_list) == 1 and len(extensive_list) == 1:
            self.get_entity_map(entity, self.entity_android[aosp_list[0]])
            return aosp_list[0]
        else:
            # 匿名类
            if entity.category == Constant.E_class and entity.anonymous != -1:
                for item_id in aosp_list:
                    if self.entity_android[item_id].raw_type == entity.raw_type and \
                            self.entity_android[self.entity_android[item_id].anonymous].name == \
                            self.entity_extensive[entity.anonymous].name:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            # 类或接口
            elif entity.category == Constant.E_class or entity.category == Constant.E_interface:
                for item_id in aosp_list:
                    if self.entity_android[item_id].abstract == entity.abstract:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            # 匿名类子实体
            elif Constant.anonymous_class in entity.qualifiedName:
                map_parent_anonymous_class = get_parent_anonymous_class(entity.id, self.entity_extensive).id
                for item_id in aosp_list:
                    aosp_parent_anonymous_class = get_parent_anonymous_class(item_id,
                                                                             self.entity_android).entity_mapping
                    if aosp_parent_anonymous_class == map_parent_anonymous_class:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            # 这里把成员变量 与 局部变量都单独抽出来
            elif entity.category == Constant.E_method or entity.category == Constant.E_variable:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_names == search_param and \
                            (not (entity.not_aosp == 0 and entity.is_intrusive == 0) or
                             (self.entity_android[item_id].parameter_types == entity.parameter_types)):
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            else:
                return aosp_list[0]
            return -1

    # get entity mapping
    def get_entity_mapping(self, entity: Entity, search_name: str, search_param_name: str, search_file: str,
                           aosp_entity_set: defaultdict, extensive_entity_set: defaultdict):
        if entity.get_ownership() == Constant.Owner_actively_native:
            pass

    # Get entity mapping relationship
    def get_entity_map(self, extensive_entity: Entity, native_entity: Entity):
        extensive_entity.set_entity_mapping(native_entity.id)
        extensive_entity.set_entity_mapping_file(native_entity.file_path)
        extensive_entity.set_entity_mapping_line(native_entity.start_line)
        native_entity.set_entity_mapping(extensive_entity.id)

    # get relation ownership
    def get_relation_ownership(self):
        print('get relation ownership')
        temp_aosp_relation_map = {}
        for relation in self.relation_android:
            temp_aosp_relation_map[str(relation.src) + relation.rel + str(relation.dest)] = relation

        for relation in self.relation_extensive:
            src = self.entity_extensive[relation.src]
            dest = self.entity_extensive[relation.dest]
            if src.not_aosp == 1 or dest.not_aosp == 1:
                relation.set_not_aosp(1)
            else:
                is_intrusive = dest.is_intrusive if relation.rel == Constant.R_annotate else src.is_intrusive
                if is_intrusive and src.entity_mapping > -1 and dest.entity_mapping > -1:
                    # if src.entity_mapping > -1 and dest.entity_mapping > -1:
                    try:
                        if temp_aosp_relation_map[str(src.entity_mapping) + relation.rel + str(dest.entity_mapping)]:
                            relation.set_not_aosp(0)
                    except KeyError:
                        relation.set_not_aosp(1)
                else:
                    relation.set_not_aosp(0)

    # get diff and extra useful aosp 'define' dep
    def detect_facade(self):
        def concept_correct(relation: Relation):
            if relation.rel == Constant.define and self.entity_extensive[relation.src].not_aosp \
                    and not self.entity_extensive[relation.dest].not_aosp:
                if self.entity_extensive[relation.src].refactor:
                    return False
            elif relation.rel == Constant.param and self.entity_extensive[relation.src].not_aosp:
                # 伴生方法不会 有原生参数
                return False
            return True

        facade_entities = set()
        for relation in self.relation_extensive:
            src = self.entity_extensive[relation.src]
            dest = self.entity_extensive[relation.dest]
            if not concept_correct(relation):
                self.facade_relations_error.append(relation)
                continue
            if src.not_aosp + dest.not_aosp == 1:
                self.facade_relations.append(relation)
                self.diff_relations.append(relation)
                facade_entities.add(src.id)
                facade_entities.add(dest.id)
                if relation.rel == Constant.define and dest.not_aosp == 1:
                    if dest.category == Constant.E_class:
                        if dest.name != Constant.anonymous_class and src.category != Constant.E_file:
                            self.inner_extensive_class_entities.append(dest.id)
                    elif dest.category == Constant.E_method:
                        self.method_extensive_entities.append(dest.id)
                    elif dest.category == Constant.E_variable:
                        if src.category != Constant.E_method:
                            self.class_var_extensive_entities.append(dest.id)
                        else:
                            self.method_var_extensive_entities.append(dest.id)
            elif src.not_aosp + dest.not_aosp == 2:
                self.diff_relations.append(relation)
            # 依赖切面扩充 侵入式到原生
            elif src.not_aosp == 0 and dest.not_aosp == 0:
                if relation.not_aosp == 1:
                    self.diff_relations.append(relation)
                    self.facade_relations.append(relation)
                    # facade_entities.add(src.id)
                    # facade_entities.add(dest.id)
                elif relation.rel == Constant.define or relation.rel == Constant.contain:
                    self.define_relations.append(relation)
            # 临时增加聚合依赖
            if relation.rel == Constant.define:
                if src.category == Constant.E_class and dest.category == Constant.E_variable:
                    type_entity_id = dest.typed
                    if type_entity_id != -1 and \
                            self.entity_extensive[type_entity_id].not_aosp != src.not_aosp:
                        self.agg_relations.append(
                            Relation(**{"src": src.id,
                                        "values": {Constant.R_aggregate: 1, "loc": relation.loc},
                                        "dest": type_entity_id}))

        self.facade_relations.extend(self.agg_relations)
        for e_id in facade_entities:
            self.facade_entities.append(self.entity_extensive[e_id])

    # out intrusive entities info
    def out_intrusive_info(self):
        def get_count_ownership():
            total_count = {'total': 0, 'native': 0, 'obsoletely native': 0, 'intrusive': 0, 'extensive': 0, 'unsure': 0}
            file_total_count = defaultdict(partial(defaultdict, int))
            for entity in self.entity_extensive:
                if entity.is_core_entity():
                    total_count['total'] += 1
                    file_total_count[entity.file_path]['total'] += 1
                    if entity.is_intrusive == 1:
                        total_count['intrusive'] += 1
                        file_total_count[entity.file_path]['intrusive'] += 1
                    elif entity.not_aosp == 0:
                        if entity.old_aosp <= 0:
                            total_count['native'] += 1
                            file_total_count[entity.file_path]['native'] += 1
                        elif entity.old_aosp >= 1:
                            total_count['obsoletely native'] += 1
                            file_total_count[entity.file_path]['obsoletely native'] += 1
                        else:
                            total_count['unsure'] += 1
                            file_total_count[entity.file_path]['unsure'] += 1
                    elif entity.not_aosp == 1:
                        total_count['extensive'] += 1
                        file_total_count[entity.file_path]['extensive'] += 1
            return total_count, file_total_count, ['total', 'native', 'obsoletely native', 'intrusive', 'extensive',
                                                   'unsure']

        def get_intrusive_count():
            total_count = {}
            header = ['access_modify', 'final_modify', 'annotation_modify', 'modifier_modify',
                      'param_modify', 'return_type_modify', 'type_modify',
                      'import_extensive',
                      'parent_class_modify', 'parent_interface_modify',
                      'class_body_modify', 'inner_extensive_class', 'class_var_extensive', 'class_var_modify',
                      'method_body_modify', 'method_extensive', 'method_var_extensive', 'method_var_modify',
                      'Move Class', 'Rename Class',
                      'Move And Rename Class', 'Move Method', 'Rename Method',
                      'Move And Rename Method', 'Extract Method', 'Extract And Move Method', 'Rename Parameter',
                      'Add Parameter', 'Remove Parameter']
            for int_type in header:
                total_count.update({int_type: 0})

            file_total_count = defaultdict(partial(defaultdict, int))
            for extensive_entity in self.entity_extensive:
                if extensive_entity.is_intrusive and extensive_entity.entity_mapping != -1:
                    # and extensive_entity.not_aosp == 0:
                    native_entity = self.entity_android[extensive_entity.entity_mapping]
                    # 提取方法不识别签名的修改
                    if extensive_entity.category == Constant.E_method and extensive_entity.id != native_entity.entity_mapping:
                        extensive_entity.set_intrusive_modify('extracted', '-')
                        self.refactor_entities_new['extract'].append(extensive_entity.id)
                        total_count['Extract Method'] += 1
                        file_total_count[extensive_entity.file_path]['Extract Method'] += 1
                        continue
                    if extensive_entity.hidden:
                        source_hd = Constant.hidden_map(native_entity.hidden)
                        update_hd = Constant.hidden_map(extensive_entity.hidden)
                        if source_hd and update_hd and source_hd != update_hd:
                            self.hidden_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('hidden_modify', source_hd + '-' + update_hd)
                    if extensive_entity.accessible != native_entity.accessible:
                        self.access_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('access_modify',
                                                              native_entity.accessible + '-' + extensive_entity.accessible)
                        total_count['access_modify'] += 1
                        file_total_count[extensive_entity.file_path]['access_modify'] += 1

                    if extensive_entity.final != native_entity.final:
                        self.final_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('final_modify',
                                                              get_final(native_entity.final) + '-' + get_final(
                                                                  extensive_entity.final))
                        total_count['final_modify'] += 1
                        file_total_count[extensive_entity.file_path]['final_modify'] += 1
                    if extensive_entity.static != native_entity.static or extensive_entity.is_global != native_entity.is_global:
                        self.modifier_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('modifier_modify', '-')
                        total_count['modifier_modify'] += 1
                        file_total_count[extensive_entity.file_path]['modifier_modify'] += 1
                    if not Compare.compare_list(extensive_entity.annotations, native_entity.annotations):
                        self.annotation_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('annotation_modify',
                                                              f'{native_entity.annotations}-{extensive_entity.annotations}')
                        total_count['annotation_modify'] += 1
                        file_total_count[extensive_entity.file_path]['annotation_modify'] += 1
                    if extensive_entity.name != native_entity.name:
                        if extensive_entity.id == native_entity.entity_mapping:
                            self.refactor_entities_new["rename"].append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('rename', '-')
                    if extensive_entity.category in [Constant.E_class, Constant.E_interface]:
                        if extensive_entity.total_hash != native_entity.total_hash:
                            self.class_body_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('body_modify', '-')
                            total_count['class_body_modify'] += 1
                            file_total_count[extensive_entity.file_path]['class_body_modify'] += 1
                        if extensive_entity.parent_class != native_entity.parent_class:
                            self.parent_class_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('parent_class_modify',
                                                                  f'{native_entity.parent_class}-{extensive_entity.parent_class}')
                            total_count['parent_class_modify'] += 1
                            file_total_count[extensive_entity.file_path]['parent_class_modify'] += 1
                        if not Compare.compare_list(native_entity.parent_interface, extensive_entity.parent_interface):
                            self.parent_interface_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('parent_interface_modify',
                                                                  f'{native_entity.parent_interface}-{extensive_entity.parent_interface}')
                            total_count['parent_interface_modify'] += 1
                            file_total_count[extensive_entity.file_path]['parent_interface_modify'] += 1
                    # todo 识别方法体的修改
                    if extensive_entity.category == Constant.E_method:
                        # 有body位置可以精确识别，暂时全部标记为body change
                        self.method_body_modify_entities.append(extensive_entity.id)
                        extensive_entity.set_intrusive_modify('body_modify', '-')
                        total_count['method_body_modify'] += 1
                        file_total_count[extensive_entity.file_path]['method_body_modify'] += 1
                        if extensive_entity.parameter_names != native_entity.parameter_names:
                            self.params_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('param_modify',
                                                                  native_entity.parameter_names + '-' + extensive_entity.parameter_names)
                            total_count['param_modify'] += 1
                            file_total_count[extensive_entity.file_path]['param_modify'] += 1
                        if extensive_entity.raw_type.rsplit('.')[-1] != native_entity.raw_type.rsplit('.')[-1]:
                            self.return_type_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('return_type_modify',
                                                                  native_entity.raw_type + '-' + extensive_entity.raw_type)
                            total_count['return_type_modify'] += 1
                            file_total_count[extensive_entity.file_path]['return_type_modify'] += 1
                    if extensive_entity.category == Constant.E_variable:
                        if extensive_entity.raw_type.rsplit('.')[-1] != native_entity.raw_type.rsplit('.')[-1]:
                            self.type_modify_entities.append(extensive_entity.id)
                            extensive_entity.set_intrusive_modify('type_modify',
                                                                  native_entity.raw_type + '-' + extensive_entity.raw_type)
                            total_count['type_modify'] += 1
                            file_total_count[extensive_entity.file_path]['type_modify'] += 1
                        if extensive_entity.is_param != -1:
                            pass
                        else:
                            # 当前enre抽取变量位置，全局变量与局部变量 从变量名开始，参数则包含全部内容，因此特殊处理
                            # 如果不包含变量赋值部分，暂时不做处理
                            if extensive_entity.get_var_entity_length() == len(extensive_entity.name) and \
                                    extensive_entity.get_var_entity_length() == len(native_entity.name):
                                pass
                            else:
                                if extensive_entity.total_hash != native_entity.total_hash:
                                    if extensive_entity.name == native_entity.name:
                                        extensive_entity.set_intrusive_modify('body_modify', '-')
                                    else:
                                        # 排除法识别一部分body change
                                        if extensive_entity.modifiers == native_entity.modifiers and \
                                                extensive_entity.raw_type.rsplit('.', 1)[-1] == \
                                                native_entity.raw_type.rsplit('.', 1)[-1]:
                                            extensive_entity.set_intrusive_modify('body_modify', '-')
                            if self.entity_extensive[extensive_entity.parentId].category == Constant.E_method:
                                self.method_var_modify_entities.append(extensive_entity.id)
                                total_count['method_var_modify'] += 1
                                file_total_count[extensive_entity.file_path]['method_var_modify'] += 1
                            else:
                                self.class_var_modify_entities.append(extensive_entity.id)
                                total_count['class_var_modify'] += 1
                                file_total_count[extensive_entity.file_path]['class_var_modify'] += 1

            for rel in self.import_extensive_relation:
                if self.entity_extensive[rel.src].not_aosp == 0:
                    total_count['import_extensive'] += 1
                    file_total_count[self.entity_extensive[rel.src].file_path]['import_extensive'] += 1

            for entity_id in self.inner_extensive_class_entities:
                total_count['inner_extensive_class'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['inner_extensive_class'] += 1

            for entity_id in self.class_var_extensive_entities:
                total_count['class_var_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['class_var_extensive'] += 1

            for entity_id in self.method_extensive_entities:
                total_count['method_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['method_extensive'] += 1

            for entity_id in self.method_var_extensive_entities:
                total_count['method_var_extensive'] += 1
                file_total_count[self.entity_extensive[entity_id].file_path]['method_var_extensive'] += 1

            for move_type, move_entity_list in self.refactor_entities.items():
                for entity_id in move_entity_list:
                    self.entity_extensive[entity_id].set_intrusive_modify(move_type, "_")
                    total_count[move_type] += 1
                    file_total_count[self.entity_extensive[entity_id].file_path][move_type] += 1
            return total_count, file_total_count, header

        ownership_count, file_owner_count, owner_keys = get_count_ownership()
        intrusive_count, file_intrusive_count, intrusive_keys = get_intrusive_count()

        FileCSV.write_owner_to_csv(self.out_path, 'final_ownership', self.entity_extensive)
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'final_ownership_count',
                                  [ownership_count], 'w')
        FileCSV.write_file_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'final_ownership_file_count',
                                  file_owner_count, 'file',
                                  owner_keys)
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'intrusive_count',
                                  [intrusive_count], 'w')
        FileCSV.write_file_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'intrusive_file_count',
                                  file_intrusive_count, 'file',
                                  intrusive_keys)
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'owner_proc', self.owner_proc, 'w')
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'owner_proc_count',
                                  [self.owner_proc_count], 'w')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'param_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.params_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'access_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.access_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'final_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.final_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'class_var_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.class_var_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'method_var_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.method_var_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'class_var_extensive_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.class_var_extensive_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'annotation_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in self.annotation_modify_entities],
                                    'modify')

        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'parent_class_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.parent_class_modify_entities],
                                    'modify')

        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'),
                                    'parent_interface_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.parent_interface_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'return_type_modify_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.return_type_modify_entities],
                                    'modify')
        FileJson.write_data_to_json(os.path.join(self.out_path, 'intrusive_analysis'),
                                    [rel.to_detail_json(self.entity_extensive) for rel in
                                     self.import_extensive_relation],
                                    'add_import.json')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'inner_extensive_class_entities',
                                    [self.entity_extensive[entity_id] for entity_id in
                                     self.inner_extensive_class_entities],
                                    'modify')

        temp_ref = set()
        for _, v in self.refactor_entities.items():
            temp_ref.update(v)
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'intrusive_analysis'), 'refactor_entities',
                                    [self.entity_extensive[entity_id] for entity_id in temp_ref],
                                    'modify')

    def out_facade_info(self):
        print('output facade info')

        def info_init():
            base_info: dict = {'total_relations': len(self.relation_extensive),
                               'total_entities': len(self.entity_extensive),
                               'facade_relation': len(self.facade_relations),
                               'facade_entities': len(self.facade_entities),
                               'facade_e2n': 0, 'facade_n2e': 0,
                               'facade_n2n': 0,
                               'facade_n2n(intrusive2actively)': 0,
                               'facade_n2n(intrusive2obsolotely)': 0,
                               'facade_n2n(intrusive2intrusive)': 0,
                               }
            relation_info = {
                'all_e2n': 0, 'all_n2e': 0, 'all_n2n': 0,
            }
            rel_src = defaultdict(partial(defaultdict, int))
            for rel_type in Constant.Relations:
                relation_info[rel_type + '_e2n'] = 0
                relation_info[rel_type + '_n2e'] = 0
                relation_info[rel_type + '_n2n'] = 0
            relation_info.update({'Define_e': 0, 'Parameter_e': 0})
            entity_info = {}
            for ent_cat in Constant.entities:
                entity_info.update({ent_cat: [0, 0]})

            for relation in self.relation_extensive:
                rel_src[relation.rel][relation.src] += 1

            return base_info, relation_info, entity_info, rel_src

        def get_index(relation: Relation) -> str:
            src_owner = self.entity_extensive[relation.src].not_aosp
            dest_owner = self.entity_extensive[relation.dest].not_aosp

            def get_index_str(index: int):
                if index:
                    return 'e'
                else:
                    return 'n'

            # if is_agg:
            #     return get_index_str(src_owner) + '2' + get_index_str(
            #         self.entity_extensive[self.entity_extensive[relation.dest].typed].not_aosp)

            """
            特殊情况处理
            
            情况1：注解依赖的方向调整，调用src和dest实体
            
            情况2：过滤概念上就无法理解的错误，如伴生实体定义原生实体，伴生方法 有原生参数
            
            
            
            """
            if relation.rel == Constant.R_annotate:
                return get_index_str(dest_owner) + '2' + get_index_str(src_owner)
            elif relation.rel == Constant.define:
                if self.entity_extensive[relation.src].not_aosp:
                    if self.entity_extensive[relation.src].refactor:
                        return get_index_str(src_owner) + '2' + get_index_str(dest_owner)
                    else:
                        # 伴生实体 不会定义原生实体
                        return 'e'
            elif relation.rel == Constant.param and self.entity_extensive[relation.src].not_aosp:
                # 伴生方法不会 有原生参数
                return 'e'
            return get_index_str(src_owner) + '2' + get_index_str(dest_owner)

        # 临时添加 聚合 依赖
        def get_key(relation: Relation) -> str:
            rel_type = relation.rel
            # if is_agg:
            #     rel_type = 'Aggregate'
            return rel_type + '_' + get_index(relation)

        # start output
        facade_relations_divide_ownership = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        facade_relations_filter = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        # facade_relations_module = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        facade_relations_module = {}
        # relations_module_vendor = {'e2e': [], 'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        relations_module_vendor = {}

        source_facade_relations_filter = []
        source_facade_relations_module = {}
        source_relations_module_vendor = {}

        source_facade_relation: Dict[str, List[Relation]] = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
        facade_base_info, facade_relation_info, facade_entity_info, rel_src_map = info_init()

        for rel in self.facade_relations:
            facade_relation_info[get_key(rel)] += 1
            facade_relations_divide_ownership[get_index(rel)].append(rel.to_detail_json(self.entity_extensive))
            source_facade_relation[get_index(rel)].append(rel)
            rel.set_facade(get_index(rel))
            # 核心文件切面
            if (StringUtils.find_str_in_list(self.entity_extensive[rel.src].file_path, Constant.core_list)) or \
                    (StringUtils.find_str_in_list(self.entity_extensive[rel.dest].file_path, Constant.core_list)):
                source_facade_relations_filter.append(rel)
                facade_relations_filter[get_index(rel)].append(rel.to_detail_json(self.entity_extensive))
            # 动态圈定的文件切面
            for module_name, module_list in Constant.module_list.items():
                if module_name not in source_facade_relations_module.keys():
                    source_facade_relations_module[module_name] = []
                    facade_relations_module[module_name] = {'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
                if StringUtils.find_str_in_short_list(self.entity_extensive[rel.src].file_path, module_list) or \
                        StringUtils.find_str_in_short_list(self.entity_extensive[rel.dest].file_path, module_list):
                    # csv格式输出
                    source_facade_relations_module[module_name].append(rel)
                    # json 格式输出
                    facade_relations_module[module_name][get_index(rel)].append(
                        rel.to_detail_json(self.entity_extensive))
            src_file = self.entity_extensive[rel.src].file_path
            dest_file = self.entity_extensive[rel.dest].file_path
            if src_file != "" and dest_file != "":
                try:
                    self.facade_relations_on_file[src_file]['beSrc'].append(
                        rel.to_simple_detail_json(self.entity_extensive))
                except KeyError:
                    self.facade_relations_on_file[src_file] = {'beSrc': [], 'beDest': []}
                    self.facade_relations_on_file[src_file]['beSrc'].append(
                        rel.to_simple_detail_json(self.entity_extensive))
                try:
                    self.facade_relations_on_file[dest_file]['beDest'].append(
                        rel.to_simple_detail_json(self.entity_extensive))
                except KeyError:
                    self.facade_relations_on_file[dest_file] = {'beSrc': [], 'beDest': []}
                    self.facade_relations_on_file[dest_file]['beDest'].append(
                        rel.to_simple_detail_json(self.entity_extensive))
        for rel in self.diff_relations:
            src = self.entity_extensive[rel.src]
            dest = self.entity_extensive[rel.dest]
            if src.not_aosp + dest.not_aosp != 2:
                continue
            for module_name, module_list in Constant.module_list.items():
                if module_name not in source_relations_module_vendor.keys():
                    source_relations_module_vendor[module_name] = []
                    relations_module_vendor[module_name] = {'e2e': [], 'e2n': [], 'n2e': [], 'n2n': [], 'e': []}
                if StringUtils.find_str_in_short_list(self.entity_extensive[rel.src].file_path, module_list) ^ \
                        StringUtils.find_str_in_short_list(self.entity_extensive[rel.dest].file_path, module_list):
                    # csv格式输出
                    source_relations_module_vendor[module_name].append(rel)
                    # json 格式输出
                    relations_module_vendor[module_name][get_index(rel)].append(
                        rel.to_detail_json(self.entity_extensive))

        # for rel in self.agg_relations:
        #     facade_relation_info[get_key(rel, True)] += 1
        # 聚合重复计数了 define依赖
        # facade_relations_divide_ownership[get_index(rel, True)].append(rel.to_detail_json(self.entity_extensive))
        # source_facade_relation[get_index(rel, True)].append(rel)

        facade_base_info['facade_n2e'] = len(facade_relations_divide_ownership['n2e'])
        facade_base_info['facade_e2n'] = len(facade_relations_divide_ownership['e2n'])
        facade_base_info['facade_n2n'] = len(facade_relations_divide_ownership['n2n'])

        # 侵入式调用原生(intrusive obsoletely actively)的情况
        for rel in facade_relations_divide_ownership['n2n']:
            if rel['dest']['ownership'] == 'actively native':
                facade_base_info['facade_n2n(intrusive2actively)'] += 1
            elif rel['dest']['ownership'] == 'intrusive native':
                facade_base_info['facade_n2n(intrusive2intrusive)'] += 1
            else:
                facade_base_info['facade_n2n(intrusive2obsolotely)'] += 1

        # 侵入式调用原生中 属于原生以及属于扩展的情况
        facade_i2n = defaultdict(partial(defaultdict, partial(defaultdict, int)))
        for ent in self.entity_extensive:
            if ent.is_intrusive == 1:
                for rel_type in Constant.Relations:
                    facade_i2n[ent.id][rel_type]['n2a'] = rel_src_map[rel_type][ent.id]
        for rel in source_facade_relation['n2n']:
            facade_i2n[rel.src][rel.rel]['e_n2n'] += 1
        entities = facade_i2n.keys()
        for rel in source_facade_relation['n2e']:
            if rel.src in entities:
                facade_i2n[rel.src][rel.rel]['n2e'] += 1

        res_n2n = []
        res_n2n_source = []
        for ent_id, rel_info in facade_i2n.items():
            temp_n2n = {'entity_id': ent_id, 'total_nat_n2n': 0, 'total_ext_n2n': 0}
            temp_n2n_source = {'entity_id': ent_id, 'total_nat_n2n': 0, 'total_ext_n2n': 0}
            temp_total_n_n2n = 0
            temp_total_e_n2n = 0
            for rel_type in Constant.Relations:
                n2a = rel_src_map[rel_type][ent_id]
                n2e = facade_i2n[ent_id][rel_type]['n2e']
                e_n2n = facade_i2n[ent_id][rel_type]['e_n2n']
                n_n2n = n2a - n2e - e_n2n

                temp_total_n_n2n += n_n2n
                temp_total_e_n2n += e_n2n

                temp_n2n.update(
                    {f'nat_n2n_{rel_type}': n_n2n,
                     f'ext_n2n_{rel_type}': e_n2n})
                temp_n2n_source.update(
                    {f'n2a_{rel_type}': n2a,
                     f'n2e_{rel_type}': n2e,
                     f'nat_n2n_{rel_type}': n_n2n,
                     f'ext_n2n_{rel_type}': e_n2n})
            temp_n2n['total_nat_n2n'] = temp_total_n_n2n
            temp_n2n['total_ext_n2n'] = temp_total_e_n2n
            temp_n2n_source['total_nat_n2n'] = temp_total_n_n2n
            temp_n2n_source['total_ext_n2n'] = temp_total_e_n2n
            res_n2n.append(temp_n2n)
            res_n2n_source.append(temp_n2n_source)
        res_n2n_stat = {'total_intrusive': len(res_n2n), 'e_0': 0, 'e_1-5': 0, 'e_6-10': 0, 'e_11-': 0}
        count_n_n2n = 0
        count_e_n2n = 0
        for info in res_n2n:
            n_n2n = info['total_nat_n2n']
            e_n2n = info['total_ext_n2n']
            count_n_n2n += n_n2n
            count_e_n2n += e_n2n
            if e_n2n == 0:
                res_n2n_stat['e_0'] += 1
            elif 1 <= e_n2n <= 5:
                res_n2n_stat['e_1-5'] += 1
            elif 6 <= e_n2n <= 10:
                res_n2n_stat['e_6-10'] += 1
            else:
                res_n2n_stat['e_11-'] += 1

        facade_base_info['facade_relation'] = facade_base_info['facade_n2e'] + facade_base_info['facade_e2n'] + \
                                              facade_base_info['facade_n2n']
        facade_relation_info['all_e2n'] = facade_base_info['facade_e2n']
        facade_relation_info['all_n2e'] = facade_base_info['facade_n2e']
        facade_relation_info['all_n2n'] = facade_base_info['facade_n2n']

        for ent in self.facade_entities:
            facade_entity_info[ent.category][ent.not_aosp] += 1
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_base_info_count',
                                  [facade_base_info], 'w')
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_relation_info_count',
                                  [facade_relation_info], 'w')
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_entity_info_count',
                                  [facade_entity_info], 'w')
        FileCSV.write_entity_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_info_entities',
                                    self.facade_entities, 'modify')
        facade_relations_divide_ownership.pop('e')

        # json 格式输出依赖切面
        FileJson.write_to_json(self.out_path, facade_relations_divide_ownership, 'facade')
        FileJson.write_to_json(self.out_path, facade_relations_filter, 'facade_core')
        for module_name, res in facade_relations_module.items():
            FileJson.write_to_json(os.path.join(self.out_path, 'facade_module'), res, f'facade_module_{module_name}')
        for module_name, res in relations_module_vendor.items():
            FileJson.write_to_json(os.path.join(self.out_path, 'facade_module'), res,
                                   f'facade_module_to_vendor_{module_name}')

        # csv格式输出依赖切面
        FileCSV.write_dict_to_csv(self.out_path, 'facade',
                                  [rel.to_csv(self.entity_extensive) for rel in self.facade_relations], 'w')
        FileCSV.write_dict_to_csv(self.out_path, 'facade_core',
                                  [rel.to_csv(self.entity_extensive) for rel in source_facade_relations_filter], 'w')
        for module_name, res in source_facade_relations_module.items():
            FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_module'), f'facade_module_{module_name}',
                                      [rel.to_csv(self.entity_extensive) for rel in res], 'w')
        for module_name, res in source_relations_module_vendor.items():
            FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_module'),
                                      f'facade_module_to_vendor_{module_name}',
                                      [rel.to_csv(self.entity_extensive) for rel in res], 'w')

        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_n2n_count', res_n2n, 'w')
        FileCSV.write_dict_to_csv(os.path.join(self.out_path, 'facade_analysis'), 'facade_n2n_stat', [res_n2n_stat],
                                  'w')

        # project = {'project': self.out_path.rsplit('\\')[-1]}
        # temp_base = project.copy()
        # temp_base.update(facade_base_info)
        # temp_rel = project.copy()
        # temp_rel.update(facade_relation_info)
        # temp_n2n_stat = project.copy()
        # temp_n2n_stat.update(res_n2n_stat)
        # temp_n2n_rel_stat = project.copy()
        # temp_n2n_rel_stat.update(res_n2n_rel_stat)
        # FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_base_info_count', [temp_base], 'a')
        # FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_relation_info_count', [temp_rel], 'a')
        # FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_n2n_stat', [temp_n2n_stat], 'a')
        # FileCSV.write_dict_to_csv('D:\\Honor\\match_res', 'facade_n2n_rel_stat', [temp_n2n_rel_stat], 'a')


# valid entity map
def valid_entity_mapping(entity: Entity, search_name: str, search_param: str):
    return entity.qualifiedName == search_name and entity.parameter_names == search_param


# get parent
def get_parent_entity(entity: int, entity_set: List[Entity]):
    return entity_set[entity_set[entity].parentId]


# get parent Anonymous_class
def get_parent_anonymous_class(entity: int, entity_set: List[Entity]):
    temp = entity
    while entity_set[temp].name != Constant.anonymous_class:
        temp = get_parent_entity(temp, entity_set).id
        print("\r", end="")
        print('parent', temp, end="")
    return entity_set[temp]


def get_final(is_final: bool):
    if is_final:
        return 'final'
    return ''

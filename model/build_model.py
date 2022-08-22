import os.path
from typing import List, Dict
from collections import defaultdict
from functools import partial
from model.entity import Entity, set_package, set_parameters
from model.relation import Relation
from model.entity_owner import EntityOwner
from model.blamer.entity_tracer import BaseState
from utils import Constant, FileCSV, FileJson

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
    params_modify_entities: List[int]
    hidden_modify_entities: List[int]
    access_modify_entities: List[int]
    final_modify_entities: List[int]
    var_extensive_entities: List[int]
    var_modify_entities: List[int]
    var_modify_method_entities: List[int]
    body_modify_entities: List[int]
    import_extensive_relation: List[Relation]

    refactor_entities: Dict[str, List[int]]
    facade_relations: List[Relation]
    facade_entities: List[Entity]
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
        self.params_modify_entities = []
        self.hidden_modify_entities = []
        self.access_modify_entities = []
        self.final_modify_entities = []
        self.var_extensive_entities = []
        self.var_modify_entities = []
        self.var_modify_method_entities = []
        self.body_modify_entities = []
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
        self.facade_relations = []
        self.facade_entities = []
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
                self.owner_proc.append(entity.to_csv())
        # init dep
        print("start init model deps")
        import_relation_set = defaultdict(int)
        print("     get aosp dep")
        for item in cells_android:
            relation = Relation(**item)
            self.relation_android.append(relation)
            if relation.rel == Constant.R_import:
                import_relation_set[relation.to_str(self.entity_android)] = 1
        print("     get assi dep")
        temp_param = defaultdict(list)
        temp_define = defaultdict(list)
        for item in cells_assi:
            relation = Relation(**item)
            self.relation_assi.append(relation)
            if relation.rel == Constant.param:
                temp_param[relation.src].append(self.entity_assi[relation.dest])
                self.entity_assi[relation.dest].set_is_param(1)
            elif relation.rel == Constant.define:
                temp_define[relation.src].append(self.entity_assi[relation.dest])
            elif relation.rel == Constant.R_import:
                if import_relation_set[relation.to_str(self.entity_assi)] != 1:
                    self.import_extensive_relation.append(relation)

        # data get -- blame
        print('start init owner from blame')
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = self.get_blame_data()
        print('get possible refactor entity')
        possible_refactor_entities = []
        possible_refactor_entities.extend(intrusive_entities.values())
        possible_refactor_entities.extend(old_intrusive_entities.values())
        possible_refactor_entities.extend(pure_accompany_entities.values())
        refactor_list = self.entity_owner.re_divide_owner(possible_refactor_entities)
        print('get entity owner')
        # first get entity owner
        print('     first get entity owner')
        self.first_owner(aosp_entity_set, assi_entity_set, all_entities, all_native_entities,
                         old_native_entities, old_update_entities, intrusive_entities,
                         old_intrusive_entities, pure_accompany_entities, refactor_list,
                         temp_define, temp_param)

        print('get filter relation set')
        self.set_dep_assi()

        # query set build
        print('get relation search dictionary')
        self.query_map_build(self.diff_relations, self.define_relations)

        print('  output entities owner and intrusive info')
        self.out_intrusive_info()

        print('output facade info')
        self.out_facade_info()

    # Get data of blame
    def get_blame_data(self):
        return self.entity_owner.divide_owner()

    # get diff and extra useful aosp 'define' dep
    def set_dep_assi(self):
        facade_entities = set()
        for relation in self.relation_assi:

            src = self.entity_assi[relation.src]
            dest = self.entity_assi[relation.dest]
            if src.not_aosp == 1 or dest.not_aosp == 1:
                relation.set_not_aosp(1)
                self.diff_relations.append(relation)
                if src.not_aosp + dest.not_aosp == 1:
                    self.facade_relations.append(relation)
                    facade_entities.add(src.id)
                    facade_entities.add(dest.id)
                    if src.category != Constant.E_method and dest.category == Constant.E_variable and \
                            relation.rel == Constant.define and dest.not_aosp == 1:
                        self.var_extensive_entities.append(dest.id)
            elif relation.rel == Constant.define:
                self.define_relations.append(relation)
        for e_id in facade_entities:
            self.facade_entities.append(self.entity_assi[e_id])

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

    # diff & blame
    def first_owner(self, aosp_entity_map, assi_entity_map, all_entities: dict, all_native_entities: dict,
                    old_native_entities: dict, old_update_entities: dict, intrusive_entities: dict,
                    old_intrusive_entities: dict, pure_accompany_entities: dict, refactor_list: Dict[int, list],
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

        def detect_ownership(ent: Entity, all_refactor_info: Dict[int, list], src_name: str, src_param: str):
            try:
                ent_refactor_info = all_refactor_info[ent.id][1]
                detect_refactor_entities(ent, ent_refactor_info, all_refactor_info)
            except KeyError:
                detect_un_refactor_entities(ent, src_name, src_param)

        def detect_git_must_native(ent: Entity):
            if ent.id not in keys_all_entities:
                return 1

        def detect_refactor_entities(ent: Entity, ent_refactor_info: list, all_refactor_info: Dict[int, list]):
            def detect_refactor_entities_son(child_entity_set: List[Entity], outer_ref_name: str, outer_ref_param: str):
                for child_ent in child_entity_set:
                    child_ent.set_refactor({'type': 'parent_ref'})
                    self.owner_proc[child_ent.id]['refactor'] = 'parent_ref'
                    child_source_qualified_name = outer_ref_name + '.' + child_ent.name
                    if child_ent.category == Constant.E_method:
                        child_source_param = child_ent.parameter_names
                    else:
                        child_source_param = outer_ref_param
                    detect_ownership(child_ent, all_refactor_info, child_source_qualified_name, child_source_param)
                    detect_refactor_entities_son(child_define[child_ent.id] + child_param[child_ent.id],
                                                 child_source_qualified_name, child_source_param)

            move_list = set()
            self.owner_proc_count['refactor'] += 1
            for move in ent_refactor_info:
                move_type: str = move[0]
                source_state: BaseState = move[1]
                dest_state: BaseState = move[2]
                print('    ', move_type, source_state.longname(), dest_state.longname())
                dep_diff_res = self.graph_differ(ent, source_state.longname(), source_state.get_param(),
                                                 aosp_entity_map, assi_entity_map)
                if dep_diff_res == -1 and ent.id in keys_pure_accompany_entities:
                    ent.set_honor(1)
                    self.owner_proc[ent.id]['dep_diff'] = '1'
                    self.owner_proc[ent.id]['git_blame'] = 'extension refactor'
                    continue
                ent.set_refactor(
                    {'type': move_type, 'source_name': source_state.longname(),
                     'source_param': source_state.get_param()})
                move_list.add(move_type)
                if move_type in MoveClassRefactoring:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in MoveMethodRefactorings:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in ExtractMethodRefactorings:
                    ent.set_honor(1)
                    ent.set_intrusive(1)
                    for ent in child_param[ent.id]:
                        ent.set_honor(1)
                    detect_refactor_entities_son(child_define[ent.id], source_state.longname(),
                                                 source_state.get_param())
                elif move_type in MoveMethodParamRefactorings:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    detect_refactor_entities_son(child_define[ent.id] + child_param[ent.id], source_state.longname(),
                                                 source_state.get_param())
                else:
                    ent.set_honor(0)
                    ent.set_intrusive(1)
                    self.owner_proc[ent.id]['dep_diff'] = 'null'
                    self.owner_proc[ent.id]['git_blame'] = 'other refactor'

            self.owner_proc[ent.id]['refactor'] = ent.refactor
            for move in move_list:
                self.owner_proc_count[move] += 1
                self.refactor_entities[move].append(ent.id)

        def detect_un_refactor_entities(ent: Entity, source_name: str, source_param: str):
            if ent.not_aosp != -2:
                self.owner_proc_count['parent_ref'] += 1
                return

            dep_diff_res = self.graph_differ(ent, source_name, source_param, aosp_entity_map,
                                             assi_entity_map)
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

        for entity in self.entity_assi:
            self.owner_proc[entity.id]['refactor'] = 'null'
            if entity.above_file_level():
                entity.set_honor(-1)
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
            elif detect_git_must_native(entity):
                entity.set_honor(0)
                self.owner_proc[entity.id]['dep_diff'] = 'any'
                self.owner_proc[entity.id]['git_blame'] = '000'
                self.owner_proc_count['dep_any'] += 1
                self.owner_proc_count['git_pure_native'] += 1
            else:
                detect_ownership(entity, refactor_list, entity.qualifiedName, entity.parameter_names)

    def load_owner_from_catch(self):
        owners = FileCSV.read_from_file_csv(os.path.join(self.entity_owner.out_path, 'final_ownership.csv'))
        for owner in owners:
            self.entity_assi[int(owner[0])].set_honor(int(owner[1]))
            self.entity_assi[int(owner[0])].set_old_aosp(int(owner[2]))
            self.entity_assi[int(owner[0])].set_intrusive(int(owner[3]))
            if int(owner[3]) == 1:
                self.entity_assi[int(owner[0])].set_entity_mapping(int(owner[7]))
                self.get_entity_map(self.entity_assi[int(owner[0])], self.entity_android[int(owner[7])])

    # graph differ
    def graph_differ(self, entity: Entity, search_name: str, search_param: str, aosp_entity_set: defaultdict,
                     assi_entity_set: defaultdict):
        aosp_list: List[int] = aosp_entity_set[entity.category][search_name]
        assi_list: List[int] = assi_entity_set[entity.category][entity.qualifiedName]
        if not aosp_list:
            return -1
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
                map_parent_anonymous_class = get_parent_anonymous_class(entity.id, self.entity_assi).id
                for item_id in aosp_list:
                    aosp_parent_anonymous_class = get_parent_anonymous_class(item_id,
                                                                             self.entity_android).entity_mapping
                    if aosp_parent_anonymous_class == map_parent_anonymous_class:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            elif entity.category == Constant.E_method or entity.category == Constant.E_variable:
                for item_id in aosp_list:
                    if self.entity_android[item_id].parameter_names == search_param:
                        self.get_entity_map(entity, self.entity_android[item_id])
                        return item_id
            else:
                return aosp_list[0]
            return -1

    # Get entity mapping relationship
    def get_entity_map(self, assi_entity: Entity, native_entity: Entity):
        assi_entity.set_entity_mapping(native_entity.id)
        native_entity.set_entity_mapping(assi_entity.id)
        # storage special entities
        if assi_entity.hidden:
            source_hd = Constant.hidden_map(native_entity.hidden)
            update_hd = Constant.hidden_map(assi_entity.hidden)
            if source_hd and update_hd and source_hd != update_hd:
                self.hidden_modify_entities.append(assi_entity.id)
                assi_entity.set_intrusive_modify('hidden_modify', source_hd + '-' + update_hd)
        if assi_entity.accessible != native_entity.accessible:
            self.access_modify_entities.append(assi_entity.id)
            assi_entity.set_intrusive_modify('access_modify',
                                             native_entity.accessible + '-' + assi_entity.accessible)
        if assi_entity.final != native_entity.final:
            self.final_modify_entities.append(assi_entity.id)
            assi_entity.set_intrusive_modify('final_modify',
                                             get_final(native_entity.final) + '-' + get_final(
                                                 assi_entity.final))
        if assi_entity.category == Constant.E_method:
            self.body_modify_entities.append(assi_entity.id)
            assi_entity.set_intrusive_modify('body_modify', '-')
            if assi_entity.parameter_names != native_entity.parameter_names:
                self.params_modify_entities.append(assi_entity.id)
                assi_entity.set_intrusive_modify('param_modify',
                                                 native_entity.parameter_names + '-' + assi_entity.parameter_names)
        if assi_entity.category == Constant.E_variable:
            if self.entity_assi[assi_entity.parentId].category == Constant.E_method:
                self.var_modify_method_entities.append(assi_entity.id)
                assi_entity.set_intrusive_modify('var_modify_method', '-')
            else:
                self.var_modify_entities.append(assi_entity.id)
                assi_entity.set_intrusive_modify('var_modify', '-')

    # out intrusive entities info
    def out_intrusive_info(self):
        def get_count_ownership():
            total_count = {'total': 0, 'native': 0, 'absolutely native': 0, 'intrusive': 0, 'extensive': 0, 'unsure': 0}
            file_total_count = defaultdict(partial(defaultdict, int))
            for entity in self.entity_assi:
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
                            total_count['absolutely native'] += 1
                            file_total_count[entity.file_path]['absolutely native'] += 1
                        else:
                            total_count['unsure'] += 1
                            file_total_count[entity.file_path]['unsure'] += 1
                    elif entity.not_aosp == 1:
                        total_count['extensive'] += 1
                        file_total_count[entity.file_path]['extensive'] += 1
            return total_count, file_total_count, ['total', 'native', 'absolutely native', 'intrusive', 'extensive',
                                                   'unsure']

        def get_intrusive_count():
            total_count = defaultdict(int)
            header = ['access_modify', 'final_modify', 'param_modify', 'import_extension', 'var_extension',
                      'var_modify', 'var_modify_method', 'body_modify',
                      'Move Class', 'Rename Class',
                      'Move And Rename Class', 'Move Method', 'Rename Method',
                      'Move And Rename Method', 'Extract Method', 'Extract And Move Method', 'Rename Parameter',
                      'Add Parameter', 'Remove Parameter']

            file_total_count = defaultdict(partial(defaultdict, int))
            for entity_id in self.access_modify_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['access_modify'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['access_modify'] += 1
            for entity_id in self.final_modify_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['final_modify'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['final_modify'] += 1
            for entity_id in self.params_modify_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['param_modify'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['param_modify'] += 1
            for rel in self.import_extensive_relation:
                total_count['import_extension'] += 1
                file_total_count[self.entity_assi[rel.src].file_path]['import_extension'] += 1

            for entity_id in self.var_extensive_entities:
                total_count['var_extension'] += 1
                file_total_count[self.entity_assi[entity_id].file_path]['var_extension'] += 1

            for entity_id in self.var_modify_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['var_modify'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['var_modify'] += 1

            for entity_id in self.var_modify_method_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['var_modify_method'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['var_modify_method'] += 1

            for entity_id in self.body_modify_entities:
                if self.entity_assi[entity_id].is_intrusive:
                    total_count['body_modify'] += 1
                    file_total_count[self.entity_assi[entity_id].file_path]['body_modify'] += 1

            for move_type, move_entity_list in self.refactor_entities.items():
                for entity_id in move_entity_list:
                    total_count[move_type] += 1
                    file_total_count[self.entity_assi[entity_id].file_path][move_type] += 1
            return total_count, file_total_count, header

        ownership_count, file_owner_count, owner_keys = get_count_ownership()
        intrusive_count, file_intrusive_count, intrusive_keys = get_intrusive_count()

        FileCSV.write_owner_to_csv(self.entity_owner.out_path, 'final_ownership', self.entity_assi)
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'final_ownership_count', [ownership_count], 'w')
        FileCSV.write_file_to_csv(self.entity_owner.out_path, 'final_ownership_file_count', file_owner_count, 'file',
                                  owner_keys)
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'intrusive_count', [intrusive_count], 'w')
        FileCSV.write_file_to_csv(self.entity_owner.out_path, 'intrusive_file_count', file_intrusive_count, 'file',
                                  intrusive_keys)
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'owner_proc', self.owner_proc, 'w')
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'owner_proc_count', [self.owner_proc_count], 'w')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'param_modify_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.params_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'access_modify_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.access_modify_entities],
                                    'modify')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'final_modify_entities',
                                    [self.entity_assi[entity_id] for entity_id in self.final_modify_entities],
                                    'modify')
        temp_ref = set()
        for _, v in self.refactor_entities.items():
            temp_ref.update(v)
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'refactor_entities',
                                    [self.entity_assi[entity_id] for entity_id in temp_ref],
                                    'modify')

    def out_facade_info(self):
        facade_base_info: dict = {'total_relations': len(self.relation_assi), 'total_entities': len(self.entity_assi),
                                  'facade_relation': len(self.facade_relations),
                                  'facade_entities': len(self.facade_entities),
                                  'facade_n2e': 0, 'facade_e2n': 0,
                                  }
        facade_relation_info = {
            'all_0': 0, 'all_1': 0,
            'Call_0': 0, 'Call_1': 0, 'Define_0': 0, 'Define_1': 0, 'UseVar_0': 0, 'UseVar_1': 0,
            'Aggregate_0': 0, 'Aggregate_1': 0, 'Typed_0': 0, 'Typed_1': 0, 'Set_0': 0, 'Set_1': 0,
            'Modify_0': 0, 'Modify_1': 0,
            'Annotate_0': 0, 'Annotate_1': 0, 'Parameter_0': 0, 'Parameter_1': 0, 'Reflect_0': 0, 'Reflect_1': 0,
            'Override_0': 0, 'Override_1': 0, 'Implement_0': 0, 'Implement_1': 0, 'Inherit_0': 0, 'Inherit_1': 0,
            'Cast_0': 0, 'Cast_1': 0, 'Call non-dynamic_0': 0, 'Call non-dynamic_1': 0, 'Define_e': 0, 'Parameter_e': 0,
        }

        facade_entity_info = {
            'Method': [0, 0], 'Interface': [0, 0], 'Class': [0, 0], 'Variable': [0, 0], 'Annotation': [0, 0],
            'File': [0, 0], 'Enum': [0, 0], 'Enum Constant': [0, 0],
        }

        # 临时反转annotate依赖
        def get_index(relation: Relation) -> str:
            if relation.rel == Constant.R_annotate:
                return str(self.entity_assi[relation.dest].not_aosp)
            elif relation.rel == Constant.define:
                if self.entity_assi[relation.src].not_aosp:
                    if self.entity_assi[relation.src].refactor:
                        return str(self.entity_assi[relation.src].not_aosp)
                    else:
                        return 'e'
            elif relation.rel == Constant.param and self.entity_assi[relation.src].not_aosp:
                return 'e'
            return str(self.entity_assi[relation.src].not_aosp)

        # 临时添加 聚合 依赖
        def get_key(relation: Relation) -> str:
            rel_type = relation.rel
            if relation.rel == Constant.typed:
                if get_parent_entity(relation.src, self.entity_assi).category != Constant.E_method:
                    rel_type = 'Aggregate'
            return rel_type + '_' + get_index(relation)

        facade_relations_divide_ownership = {'0': [], '1': [], 'e': []}
        for rel in self.facade_relations:
            facade_relation_info[get_key(rel)] += 1
            facade_relations_divide_ownership[get_index(rel)].append(rel.to_detail_json(self.entity_assi))
        facade_base_info['facade_n2e'] = len(facade_relations_divide_ownership['0'])
        facade_base_info['facade_e2n'] = len(facade_relations_divide_ownership['1'])
        facade_relation_info['all_0'] = facade_base_info['facade_n2e']
        facade_relation_info['all_1'] = facade_base_info['facade_e2n']

        for ent in self.facade_entities:
            facade_entity_info[ent.category][ent.not_aosp] += 1

        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'facade_base_info_count', [facade_base_info], 'w')
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'facade_relation_info_count', [facade_relation_info], 'w')
        FileCSV.write_dict_to_csv(self.entity_owner.out_path, 'facade_entity_info_count', [facade_entity_info],
                                  'w')
        FileCSV.write_entity_to_csv(self.entity_owner.out_path, 'facade_info_entities',
                                    self.facade_entities, 'modify')
        FileJson.write_to_json(self.entity_owner.out_path, facade_relations_divide_ownership, 1)


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
    return entity_set[temp]


def get_final(is_final: bool):
    if is_final:
        return 'final'
    return ''

from typing import List
from constant.constant import Constant
from model.dependency.degree import Degree


class Entity:
    qualifiedName: str
    name: str
    id: int
    category: str
    parentId: int
    raw_type: str
    raw_type_content: str
    parameter_types: str
    parameter_names: str
    parameter_entities: List[int]
    file_path: str
    package_name: str
    not_aosp: int
    is_intrusive: int
    intrusive_modify: dict
    is_decoupling: int
    bin_path: str
    entity_mapping: int
    modifiers: List[str]
    accessible: str
    abstract: bool
    final: bool
    static: bool
    is_global: int
    innerType: list
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    body_start_line: int
    body_start_column: int
    body_end_line: int
    body_end_column: int
    hidden: List[str]
    commits: List[str]
    commits_count: dict
    refactor: List[dict]
    is_anonymous_class: bool
    anonymous: int
    old_aosp: int
    is_param: int
    typed: int
    annotations: List[str]
    parent_class: str
    parent_interface: List[str]
    called: int
    called_entities: List[int]
    call_entities: List[int]
    conflict_times: int
    conflict_blocks: int
    conflict_loc: int
    degree: Degree
    extract_to: List[int]
    children: set
    total_hash: str
    body_hash: str

    def __init__(self, **args):
        self.qualifiedName = args['qualifiedName']
        self.name = args['name']
        self.id = args['id']
        self.category = args['category']
        self.parentId = args['parentId']
        self.file_path = ""
        self.package_name = ""
        self.not_aosp = -2
        self.is_intrusive = 0
        self.entity_mapping = -1
        self.entity_mapping_file = ""
        self.entity_mapping_start_line = -1
        self.modifiers = []
        self.abstract = False
        self.static = False
        self.final = False
        self.accessible = 'null'
        self.is_decoupling = -1
        self.intrusive_modify = {}
        self.bin_path = ''
        self.commits = []
        self.commits_count = {}
        self.refactor = []
        self.old_aosp = -1
        self.is_param = -1
        self.typed = -1
        self.annotations = []
        self.parent_class = ''
        self.parent_interface = []
        self.called = 0
        self.is_anonymous_class = False
        self.conflict_times = 0
        self.conflict_blocks = 0
        self.conflict_loc = 0
        self.degree = Degree()
        self.extract_to = []
        self.called_entities = []
        self.call_entities = []
        self.children = set()
        self.total_hash = ""
        self.body_hash = ""
        self.parameter_entities = []
        self.raw_type_content = "null"
        self.outer = []
        try:
            self.start_line = args['location']['startLine']
            self.start_column = args['location']['startColumn']
            self.end_line = args['location']['endLine']
            self.end_column = args['location']['endColumn']
        except KeyError:
            self.start_line = -1
            self.start_column = -1
            self.end_line = -1
            self.end_column = -1
        try:
            self.body_start_line = args['blockLoc']['startLine']
            self.body_start_column = args['blockLoc']['startColumn']
            self.body_end_line = args['blockLoc']['endLine']
            self.body_end_column = args['blockLoc']['endColumn']
        except KeyError:
            self.body_start_line = -1
            self.body_start_column = -1
            self.body_end_line = -1
            self.body_end_column = -1
        try:
            self.file_path = args['File']
        except KeyError:
            self.file_path = ""
        try:
            self.modifiers = []
            for item in args['modifiers'].split(" "):
                self.modifiers.append(item)
            for item in Constant.accessible_list:
                if item in args['modifiers']:
                    self.accessible = item
                    break
            if Constant.M_abstract in args['modifiers']:
                self.abstract = True
            if Constant.M_final in args['modifiers']:
                self.final = True
            if Constant.M_static in args['modifiers']:
                self.static = True
        except KeyError:
            self.modifiers = []
        try:
            self.raw_type = args['rawType']
        except KeyError:
            self.raw_type = 'null'
        try:
            self.parameter_types = args['parameter']['types']
            self.parameter_names = args['parameter']['names']
        except KeyError:
            self.parameter_types = "null"
            self.parameter_names = "null"
        try:
            self.is_global = 1 if args['global'] else 0
        except KeyError:
            self.is_global = 2
        try:
            self.innerType = args['innerType']
        except KeyError:
            self.innerType = []
        try:
            self.hidden = []
            for item in args['hidden'].split(" "):
                self.hidden.append(item)
        except KeyError:
            self.hidden = []
        try:
            self.is_decoupling = args['additionalBin']['binNum']
        except KeyError:
            self.is_decoupling = 0
        try:
            self.bin_path = args['additionalBin']['binPath']
        except KeyError:
            self.bin_path = 'aosp'
        try:
            self.anonymous = args['anonymousBindVar']
        except KeyError:
            self.anonymous = -1

    def __str__(self):
        return self.category + "#" + self.qualifiedName

    def to_string(self):
        return str(self.id) + '#' + self.category + "#" + self.qualifiedName

    def to_common_string(self):
        return self.category + "#" + self.qualifiedName

    def to_csv(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'conflict_times': self.conflict_times, 'conflict_blocks': self.conflict_blocks,
                'conflict_loc': self.conflict_loc}

    def to_owner(self):
        return {'id': self.id, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp, 'isIntrusive': self.is_intrusive,
                'ownership': self.get_ownership(), 'category': self.category, 'qualifiedName': self.qualifiedName,
                'file_path': self.file_path, 'mapping': self.entity_mapping, 'modify': self.intrusive_modify}

    def handle_to_format(self, to_format: str):
        method = getattr(self, f'handle_to_{to_format}', None)
        return method()

    def handle_to_modify(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'file_path': self.file_path, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp,
                'isIntrusive': self.is_intrusive, 'intrusiveModify': self.intrusive_modify, 'refactor': self.refactor}

    def handle_to_facade(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'file_path': self.file_path, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp,
                'isIntrusive': self.is_intrusive}

    def handle_to_hash(self):
        return {'id': self.id, 'total_hash': self.total_hash, 'body_hash': self.body_hash}

    def handle_to_csv(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName}

    def handle_to_vf(self):
        category = Constant.entities.index(self.category)
        label = -1 * category if self.not_aosp > 0 else category
        return [str(self.id), str(label)]

    def handle_to_db(self):
        temp = {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'ownership': self.get_ownership(), 'name': self.name,
                'commits_count': self.commits_count}
        if self.file_path != "":
            temp['file_path'] = self.file_path
        if self.package_name != "":
            temp['packageName'] = self.package_name
        if self.start_line != -1:
            temp['location'] = {}
            temp['location']['startLine'] = self.start_line
            temp['location']['startColumn'] = self.start_column
            temp['location']['endLine'] = self.end_line
            temp['location']['endColumn'] = self.end_column
        if self.parameter_types != 'null' and self.category == Constant.E_method:
            temp['parameterTypes'] = self.parameter_types
            temp['parameterNames'] = self.parameter_names
        if self.raw_type != 'null':
            temp['rawType'] = self.raw_type
        if self.modifiers:
            temp['modifiers'] = " ".join(self.modifiers)
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        if self.hidden:
            temp['hidden'] = " ".join(self.hidden)
        if self.commits:
            temp['commits'] = self.commits
        if self.refactor:
            temp['refactor'] = self.refactor
        if self.intrusive_modify:
            temp['intrusiveModify'] = self.intrusive_modify
        if self.entity_mapping:
            temp['mapping_file'] = self.entity_mapping_file
            temp['mapping_start_line'] = self.entity_mapping_start_line
        return temp

    @classmethod
    def get_csv_header(cls):
        return ['id', 'category', 'qualifiedName', 'conflict_loc', 'conflict_blocks', 'conflict_times']

    def get_var_entity_length(self):
        return self.end_column - self.start_column + 1 if self.start_line == self.end_line else -1

    def get_ownership(self):
        if self.not_aosp == 1 or self.not_aosp == -2:
            return Constant.Owner_extensive
        elif self.is_intrusive == 1:
            return Constant.Owner_intrusive_native
        elif self.old_aosp == 1:
            return Constant.Owner_obsoletely_native
        else:
            return Constant.Owner_actively_native

    def toJson(self):
        temp = {'id': self.id, 'not_aosp': self.not_aosp, 'is_decoupling': self.is_decoupling,
                'old_aosp': self.old_aosp, 'isIntrusive': self.is_intrusive,
                'ownership': self.get_ownership(), 'entity_mapping': self.entity_mapping, 'category': self.category,
                'qualifiedName': self.qualifiedName, 'called_times': self.called, 'name': self.name,
                'commits_count': self.commits_count, 'degree': self.degree.__dict__}
        if self.file_path != "":
            temp['File'] = self.file_path
        if self.package_name != "":
            temp['packageName'] = self.package_name
        if self.start_line != -1:
            temp['location'] = {}
            temp['location']['startLine'] = self.start_line
            temp['location']['startColumn'] = self.start_column
            temp['location']['endLine'] = self.end_line
            temp['location']['endColumn'] = self.end_column
        if self.parameter_types != 'null' and self.category == Constant.E_method:
            temp['parameterTypes'] = self.parameter_types
            temp['parameterNames'] = self.parameter_names
        if self.raw_type != 'null':
            temp['rawType'] = self.raw_type
        if self.modifiers:
            temp['modifiers'] = " ".join(self.modifiers)
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        if self.hidden:
            temp['hidden'] = " ".join(self.hidden)
        if self.commits:
            temp['commits'] = self.commits
        if self.refactor:
            temp['refactor'] = self.refactor
        if self.intrusive_modify:
            temp['intrusiveModify'] = self.intrusive_modify
        return temp

    def to_detail(self):
        temp = {
            'ownership': self.get_ownership(), 'category': self.category,
            'qualifiedName': self.qualifiedName, 'name': self.name, }
        if self.file_path != "":
            temp['File'] = self.file_path
        if self.start_line != -1:
            temp['location'] = {}
            temp['location']['startLine'] = self.start_line
            temp['location']['startColumn'] = self.start_column
            temp['location']['endLine'] = self.end_line
            temp['location']['endColumn'] = self.end_column
        if self.parameter_types != 'null' and self.category == Constant.E_method:
            temp['parameterTypes'] = self.parameter_types
            temp['parameterNames'] = self.parameter_names
        if self.raw_type != 'null':
            temp['rawType'] = self.raw_type
        if self.modifiers:
            temp['modifiers'] = " ".join(self.modifiers)
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        if self.hidden:
            temp['hidden'] = " ".join(self.hidden)
        return temp

    def set_honor(self, not_aosp: int):
        self.not_aosp = not_aosp

    def set_intrusive(self, intrusive: int):
        self.is_intrusive = intrusive

    def set_intrusive_modify(self, intrusive_type: str, intrusive_value: str):
        self.intrusive_modify[intrusive_type] = intrusive_value

    def set_entity_mapping(self, entity_id: int):
        self.entity_mapping = entity_id

    def set_entity_mapping_file(self, file_path: str):
        self.entity_mapping_file = file_path

    def set_entity_mapping_line(self, start: int):
        self.entity_mapping_start_line = start

    def set_package_name(self, package_name: str):
        self.package_name = package_name

    def set_annotations(self, annotation: str):
        self.annotations.append(annotation)

    def set_typed(self, typed: int):
        self.typed = typed

    def set_parent_param(self, parameter_types: str, parameter_names: str):
        self.parameter_types = parameter_types
        self.parameter_names = parameter_names

    def set_param_entities(self, param: int):
        self.parameter_entities.append(param)

    def set_commits(self, commits: List[str]):
        self.commits = commits

    def set_commits_count(self, count: dict):
        self.commits_count = count

    def set_refactor(self, refactor: dict):
        def to_string(ref: dict):
            to_str = ''
            for k, v in ref.items():
                to_str += str(v)

        for ref in self.refactor:
            if to_string(refactor) == to_string(ref):
                return
        self.refactor.append(refactor)

    def set_old_aosp(self, old_aosp: int):
        self.old_aosp = old_aosp

    def set_is_param(self, is_param: int):
        self.is_param = is_param

    def set_parent_class(self, parent_class: str):
        self.parent_class = parent_class

    def set_parent_interface(self, parent_interface: str):
        self.parent_interface.append(parent_interface)

    def set_called_count(self, entID):
        self.called += 1
        self.called_entities.append(entID)

    def set_call_count(self, entID):
        self.call_entities.append(entID)

    def set_hidden(self, hidden: list):
        self.hidden = hidden

    def set_anonymous_class(self, is_anonymous: bool):
        self.is_anonymous_class = is_anonymous

    def set_conf_data(self, times, blocks, loc):
        self.conflict_times = times
        self.conflict_blocks = blocks
        self.conflict_loc = loc

    def set_degree(self, **kwargs):
        self.degree.handle_set_degree(**kwargs)

    def set_out_ent(self, rel: int):
        self.outer.append(rel)

    def set_extract_to(self, entity_id):
        self.extract_to.append(entity_id)

    def set_children(self, entity_id):
        self.children.add(entity_id)

    def set_total_hash(self, hash_val):
        self.total_hash = hash_val

    def set_body_hash(self, hash_val):
        self.body_hash = hash_val

    def above_file_level(self):
        return self.category == Constant.E_file or self.category == Constant.E_package

    def is_core_entity(self):
        return self.category == Constant.E_method or self.category == Constant.E_class or self.category == Constant.E_interface or \
               self.category == Constant.E_variable

    def get_raw_type(self, content: str):
        clem = content.split(" ")
        for item in clem:
            if self.raw_type.split(".")[-1] in item:
                self.raw_type_content = item
                break


def set_package(entity: Entity, entities: List[Entity]):
    if entity.category != Constant.E_package:
        flag = True
        if entity.parentId != -1:
            temp = entities[entity.parentId]
            while temp.category != Constant.E_package:
                if temp.package_name != "":
                    entity.set_package_name(temp.package_name)
                    flag = False
                    break
                temp = entities[temp.parentId]
            if flag:
                entity.set_package_name(temp.qualifiedName)
        else:
            entity.set_package_name('null')


def set_parameters(entity: Entity, entities: List[Entity]):
    if entity.parentId != -1 and entity.category == Constant.E_variable:
        temp = entity
        while entities[temp.parentId].category == Constant.E_method:
            temp = entities[temp.parentId]
        entity.set_parent_param(temp.parameter_types, temp.parameter_names)


def get_accessible_domain(src_entity: Entity, dest_entity: Entity, entities: List[Entity]):
    # 获取节点父 类节点
    def get_parent_class_node(entity: Entity):
        if entity.category != Constant.E_class:
            if entity.parentId != -1:
                temp = entities[entity.parentId]
                while temp.category != Constant.E_class:
                    temp = entities[temp.parentId]
                return temp.id
            else:
                return -1
        else:
            return entity.id

    src_entity_parent_class_node = get_parent_class_node(src_entity)
    dest_entity_parent_class_node = get_parent_class_node(dest_entity)
    if src_entity_parent_class_node == dest_entity_parent_class_node:
        return 0
    elif src_entity.package_name == dest_entity.package_name:
        return 1
    else:
        if entities[dest_entity_parent_class_node].qualifiedName == \
                entities[dest_entity_parent_class_node].parent_class:
            return 2
        else:
            return 3

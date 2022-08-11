from typing import List
from utils.constant import Constant


class Entity:
    qualifiedName: str
    name: str
    id: int
    category: str
    parentId: int
    raw_type: str
    parameter_types: str
    parameter_names: str
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
    final: bool
    static: bool
    is_global: int
    innerType: list
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    hidden: List[str]
    commits: List[str]
    refactor: List[dict]
    anonymous: int
    old_aosp: int

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
        self.modifiers = []
        self.static = False
        self.final = False
        self.accessible = 'null'
        self.is_decoupling = -1
        self.intrusive_modify = {}
        self.bin_path = ''
        self.commits = []
        self.refactor = []
        self.old_aosp = -1
        try:
            self.start_line = args['startLine']
            self.start_column = args['startColumn']
            self.end_line = args['endLine']
            self.end_column = args['endColumn']
        except KeyError:
            self.start_line = -1
            self.start_column = -1
            self.end_line = -1
            self.end_column = -1
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

    def to_csv(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName}

    def to_owner(self):
        return {'id': self.id, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp, 'isIntrusive': self.is_intrusive,
                'category': self.category, 'qualifiedName': self.qualifiedName, 'file_path': self.file_path,
                'mapping': self.entity_mapping}

    def handle_to_format(self, to_format: str):
        method = getattr(self, f'handle_to_{to_format}', None)
        return method()

    def handle_to_modify(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'file_path': self.file_path, 'not_aosp': self.not_aosp, 'isIntrusive': self.is_intrusive,
                'intrusiveModify': self.intrusive_modify, 'refactor': self.refactor}

    def handle_to_facade(self):
        return {'id': self.id, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'file_path': self.file_path, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp,
                'isIntrusive': self.is_intrusive}

    @classmethod
    def get_csv_header(cls):
        return ['id', 'category', 'qualifiedName']

    def toJson(self):
        temp = {'id': self.id, 'not_aosp': self.not_aosp, 'old_aosp': self.old_aosp, 'category': self.category,
                'qualifiedName': self.qualifiedName, 'name': self.name, 'isIntrusive': self.is_intrusive}
        if self.file_path != "":
            temp['File'] = self.file_path
        if self.package_name != "":
            temp['packageName'] = self.package_name
        if self.start_line != -1:
            temp['startLine'] = self.start_line
            temp['startColumn'] = self.start_column
            temp['endLine'] = self.end_line
            temp['endColumn'] = self.end_column
        if self.parameter_types != 'null':
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

    def set_honor(self, not_aosp: int):
        self.not_aosp = not_aosp

    def set_intrusive(self, intrusive: int):
        self.is_intrusive = intrusive

    def set_intrusive_modify(self, intrusive_type: str, intrusive_value: str):
        self.intrusive_modify[intrusive_type] = intrusive_value

    def set_entity_mapping(self, entity_id: int):
        self.entity_mapping = entity_id

    def set_package_name(self, package_name: str):
        self.package_name = package_name

    def set_access_modify(self, access_modify: str):
        self.access_modify = access_modify

    def set_hidden_modify(self, hidden_modify: str):
        self.hidden_modify = hidden_modify

    def set_parent_param(self, parameter_types: str, parameter_names: str):
        self.parameter_types = parameter_types
        self.parameter_names = parameter_names

    def set_commits(self, commits: List[str]):
        self.commits = commits

    def set_refactor(self, refactor: dict):
        self.refactor.append(refactor)

    def set_old_aosp(self, old_aosp: int):
        self.old_aosp = old_aosp

    def above_file_level(self):
        return self.category == Constant.E_file or self.category == Constant.E_package

    def is_core_entity(self):
        return self.category == Constant.E_method or self.category == Constant.E_class or self.category == Constant.E_interface or \
               self.category == Constant.E_variable


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

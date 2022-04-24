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
    file_path: str
    not_aosp: int
    max_target_sdk: int
    is_intrusive: int
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
    aosp_hidden: int

    def __init__(self, **args):
        self.qualifiedName = args['qualifiedName']
        self.name = args['name']
        self.id = args['id']
        self.category = args['category']
        self.parentId = args['parentId']
        self.file_path = ""
        self.not_aosp = 0
        self.max_target_sdk = -1
        self.is_intrusive = 0
        self.entity_mapping = -1
        self.modifiers = []
        self.static = False
        self.final = False
        self.accessible = ''
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
            self.raw_type = ''
        try:
            self.parameter_types = args['parameterTypes']
        except KeyError:
            self.parameter_types = ""
        try:
            self.is_global = 1 if args['global'] else 0
        except KeyError:
            self.is_global = 2
        try:
            self.innerType = args['innerType']
        except KeyError:
            self.innerType = []
        try:
            self.aosp_hidden = 1 if args['aosp_hidden']['hidden'] else 0
            self.max_target_sdk = args['aosp_hidden']['maxTargetSdk']
        except KeyError:
            self.aosp_hidden = -1

    def __str__(self):
        return self.category + "#" + self.qualifiedName

    def toJson(self):
        temp = {'id': self.id, 'not_aosp': self.not_aosp, 'category': self.category,
                'qualifiedName': self.qualifiedName, 'name': self.name, 'isIntrusive': self.is_intrusive}
        if self.file_path != "":
            temp['File'] = self.file_path
        if self.start_line != -1:
            temp['startLine'] = self.start_line
            temp['startColumn'] = self.start_column
            temp['endLine'] = self.end_line
            temp['endColumn'] = self.end_column
        if self.parameter_types != '':
            temp['parameterTypes'] = self.parameter_types
        if self.raw_type != '':
            temp['rawType'] = self.raw_type
        if self.modifiers:
            temp['modifiers'] = " ".join(self.modifiers)
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        if self.aosp_hidden != -1:
            temp['hidden'] = True if self.aosp_hidden == 1 else False
            temp['maxTargetSdk'] = self.max_target_sdk
        return temp

    def set_honor(self, not_aosp: int):
        self.not_aosp = not_aosp

    def set_intrusive(self, intrusive: int):
        self.is_intrusive = intrusive

    def set_entity_mapping(self, entity_id: int):
        self.entity_mapping = entity_id

from typing import List
from utils.constant import Constant


class Entity:
    qualifiedName: str
    name: str
    id: int
    category: str
    parentId: int
    var_type: str
    file_path: str
    isHonor: int
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
    aosp_hidden: bool

    def __init__(self, **args):
        self.qualifiedName = args['qualifiedName']
        self.name = args['name']
        self.id = args['id']
        self.category = args['category']
        self.parentId = args['parentId']
        self.file_path = ""
        self.isHonor = 0
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
        except:
            self.start_line = -1
            self.start_column = -1
            self.end_line = -1
            self.end_column = -1
        try:
            self.file_path = args['File']
        except:
            self.file_path = ""
        try:
            self.modifiers = []
            for item in args['modifiers'].split(" "):
                self.modifiers.append(item)
            if self.modifiers[0] in Constant.accessible_list:
                self.accessible = self.modifiers[0]
            if Constant.M_final in self.modifiers:
                self.final = True
            if Constant.M_static in self.modifiers:
                self.static = True
        except:
            self.modifiers = []
        try:
            self.var_type = args['type']
        except:
            self.var_type = ''
        try:
            self.is_global = 1 if args['global'] else 0
        except:
            self.is_global = 2
        try:
            self.innerType = args['innerType']
        except:
            self.innerType = []
        try:
            self.aosp_hidden = args['aosp_hidden']['hidden']
        except:
            self.aosp_hidden = False

    def __str__(self):
        return self.category + "#" + self.qualifiedName

    def toJson(self):
        temp = {'id': self.id, 'isHonor': self.isHonor, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'name': self.name, 'isIntrusive': self.is_intrusive}
        if self.file_path != "":
            temp['File'] = self.file_path
        if self.start_line != -1:
            temp['startLine'] = self.start_line
            temp['startColumn'] = self.start_column
            temp['endLine'] = self.end_line
            temp['endColumn'] = self.end_column
        if self.var_type != '':
            temp['type'] = self.var_type
        if self.modifiers:
            temp['modifiers'] = " ".join(self.modifiers)
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        return temp

    def set_honor(self, isHonor: int):
        self.isHonor = isHonor

    def set_intrusive(self, intrusive: int):
        self.is_intrusive = intrusive

    def set_entity_mapping(self, entity_id: int):
        self.entity_mapping = entity_id

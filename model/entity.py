class Entity:
    qualifiedName: str
    name: str
    id: int
    category: str
    parentId: int
    var_type: str
    isHonor: int
    accessibility: str
    access_change: str
    static: int
    is_global: int
    innerType: list
    start_line: int
    start_column: int
    end_line: int
    end_column: int

    def __init__(self, **args):
        self.qualifiedName = args['qualifiedName']
        self.name = args['name']
        self.id = args['id']
        self.category = args['category']
        self.parentId = args['parentId']
        self.isHonor = -1
        self.access_change = ''
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
            self.accessibility = args['accessibility']
        except:
            self.accessibility = ''
        try:
            self.var_type = args['type']
        except:
            self.var_type = ''
        try:
            self.static = 1 if args['static'] else 0
        except:
            self.static = 2
        try:
            self.is_global = 1 if args['global'] else 0
        except:
            self.is_global = 2
        try:
            self.innerType = args['innerType']
        except:
            self.innerType = []

    def __str__(self):
        return self.category + "#" + self.qualifiedName

    def toJson(self):
        temp = {'id': self.id, 'isHonor': self.isHonor, 'category': self.category, 'qualifiedName': self.qualifiedName,
                'name': self.name}
        if self.start_line != -1:
            temp['startLine'] = self.start_line
            temp['startColumn'] = self.start_column
            temp['endLine'] = self.end_line
            temp['endColumn'] = self.end_column
        if self.var_type != '':
            temp['type'] = self.var_type
        if self.accessibility != '':
            temp['accessibility'] = self.accessibility
        if self.access_change != '':
            temp['accessChange'] = self.access_change
        if self.static != 2:
            temp['static'] = True if self.static else False
        if self.is_global != 2:
            temp['global'] = True if self.is_global else False
        return temp

    def set_honor(self, isHonor: int):
        self.isHonor = isHonor

    def set_access(self, access_change: str):
        self.access_change = access_change

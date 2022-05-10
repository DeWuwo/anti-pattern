from typing import Dict
from utils import Constant


class Relation:
    src: int
    dest: int
    rel: str
    bind_var: int
    setAccessible: int
    invoke: int
    not_aosp: int

    def __init__(self, **kwargs):
        self.bind_var = -1
        self.setAccessible = -1
        self.invoke = -1
        self.src = kwargs['src']
        self.dest = kwargs['dest']

        for key in kwargs['values']:
            if key == 'bindVar':
                self.bind_var = kwargs['values'][key]
            elif key == 'modifyAccessible':
                self.setAccessible = 1 if kwargs['values'][key] else 0
            elif key == 'invoke':
                self.invoke = 1 if kwargs['values'][key] else 0
            else:
                self.rel = key

    def toJson(self):
        relation = {self.rel: 1}
        if self.bind_var != -1:
            relation['bindVar'] = self.bind_var
        if self.rel == Constant.reflect:
            relation['setAccessible'] = True if self.setAccessible else False
            relation['invoke'] = True if self.invoke else False
        return {"src": self.src, "values": relation, "dest": self.dest}

    def __str__(self):
        return str(self.src) + self.rel + str(self.dest)

    def set_not_aosp(self, not_aosp):
        self.not_aosp = not_aosp

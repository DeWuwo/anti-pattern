from typing import Dict


class Relation:
    src: Dict
    dest: Dict
    rel: str
    bind_var: int

    def __init__(self, src, bind_var, rel, dest):
        self.src = src
        self.bind_var = bind_var
        self.rel = rel
        self.dest = dest

    def toJson(self):
        relation = {self.rel: 1}
        if self.bind_var != -1:
            relation['bindVar'] = self.bind_var
        return {"src": self.src, "values": relation, "dest": self.dest}

    def __str__(self):
        return str(self.src['id']) + self.rel + str(self.dest['id'])

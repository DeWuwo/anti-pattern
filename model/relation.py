from typing import Dict


class Relation:
    src: Dict
    dest: Dict
    rel: str

    def __init__(self, src, rel, dest):
        self.src = src
        self.rel = rel
        self.dest = dest

    def toJson(self):
        return {"src": self.src, "values": {self.rel: 1}, "dest": self.dest}

    def __str__(self):
        return str(self.src['id']) + self.rel + str(self.dest['id'])

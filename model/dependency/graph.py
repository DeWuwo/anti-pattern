import networkx as nx
from networkx import DiGraph
from typing import List

from model.dependency.entity import Entity
from model.dependency.relation import Relation


class Graph:
    entities: List[Entity]
    relations: List[Relation]
    G: DiGraph

    def __init__(self, entities: List[Entity], relations: List[Relation]):
        print('build graph')
        G = nx.DiGraph()
        self.entities = entities
        self.relations = relations
        G.add_nodes_from([(ent.id, ent.handle_to_csv()) for ent in self.entities])
        G.add_edges_from([(rel.src, rel.dest, rel.handle_to_simple_json()) for rel in self.relations])
        self.G = G

    def get_analysis(self, entity: Entity):
        kw = {'in_degree': self.G.in_degree(entity.id), 'out_degree': self.G.out_degree(entity.id)}
        entity.set_degree(**kw)

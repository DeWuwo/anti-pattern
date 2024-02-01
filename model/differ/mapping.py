from collections import defaultdict
from functools import partial
from typing import List

from model.dependency.entity import Entity
from utils import Constant


class Mapping:
    aosp_entities: List[Entity]
    extensive_entities: List[Entity]
    aosp_entities_dict: defaultdict
    extensive_entities_dict: defaultdict

    def __init__(self, aosp_entities, extensive_entities):
        self.aosp_entities = aosp_entities
        self.extensive_entities = extensive_entities
        self.aosp_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))
        self.extensive_entity_set = defaultdict(partial(defaultdict, partial(defaultdict, list)))

    def exactly_mapping(self, extensive_entities: List[Entity]):
        for entity in extensive_entities:
            aosp_list_full: List[int] = self.aosp_entities_dict[entity.category][entity.name][entity.file_path]
            extensive_list_full: List[int] = self.extensive_entities_dict[entity.category][entity.qualifiedName][
                entity.file_path]

            aosp_list: List[int] = [ent for ent in aosp_list_full if self.aosp_entities[ent].entity_mapping == -1]
            extensive_list: List[int] = [ent for ent in extensive_list_full if
                                         self.extensive_entities[ent].entity_mapping == -1]
            if not aosp_list:
                continue
            if entity.category == Constant.E_class:
                if entity.name == Constant.anonymous_class:
                    pass
                else:
                    self.entity_mapping(self.aosp_entities[aosp_list[0]], entity)
            elif entity.category == Constant.E_method:
                pass
            elif entity.category == Constant.E_variable:
                if self.extensive_entities[entity.parentId].category in [Constant.E_class, Constant.E_interface]:
                    pass
                else:
                    continue


    @classmethod
    def entity_mapping(cls, aosp_entity: Entity, extensive_entity: Entity):
        aosp_entity.set_entity_mapping(extensive_entity.id)
        extensive_entity.set_entity_mapping(aosp_entity.id)

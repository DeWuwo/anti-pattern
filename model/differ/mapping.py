from collections import defaultdict
from functools import partial
from typing import List, Dict

from model.dependency.entity import Entity
from model.blamer.entity_tracer import BaseState
from utils import Constant

MoveMethodRefactorings = {
    "Move And Rename Method": ["rename", "move"],
    "Move Method": ["move"],
    "Rename Method": ["rename"],
}

ExtractMethodRefactorings = {
    "Extract Method": ["extracted"],
    "Extract And Move Method": ["extracted", "move"]
}

MoveMethodParamRefactorings = {
    "Rename Parameter": ["param_modify"],
    "Add Parameter": ["param_modify"],
    "Remove Parameter": ["param_modify"],
}

MoveClassRefactoring = {
    "Rename Class": ["rename"],
    "Move Class": ["move"],
    "Move And Rename Class": ["rename", "move"]
}


class Mapping:
    aosp_entities: List[Entity]
    extensive_entities: List[Entity]
    aosp_entities_dict: defaultdict
    extensive_entities_dict: defaultdict
    aosp_entities_um: Dict[int, Entity]
    extensive_entities_um: Dict[int, Entity]

    def __init__(self, aosp_entities, extensive_entities, aosp_entities_set, extensive_entities_set, aosp_entities_um,
                 extensive_entities_um):
        self.aosp_entities = aosp_entities
        self.extensive_entities = extensive_entities
        self.aosp_entities_dict = aosp_entities_set
        self.extensive_entities_dict = extensive_entities_set
        self.aosp_entities_um = aosp_entities_um
        self.extensive_entities_um = extensive_entities_um

    def exactly_match(self, entity: Entity, search_name: str, search_param: str, search_file: str):
        if entity.above_file_level():
            return
        aosp_list_full: List[int] = self.aosp_entities_dict[entity.category][search_name][search_file]
        extensive_list_full: List[int] = self.extensive_entities_dict[entity.category][entity.qualifiedName][
            entity.file_path]

        aosp_list: List[int] = [ent for ent in aosp_list_full if self.aosp_entities[ent].entity_mapping == -1]
        extensive_list: List[int] = [ent for ent in extensive_list_full if
                                     self.extensive_entities[ent].entity_mapping == -1]

        aosp_list.sort()
        extensive_list.sort()

        # if not aosp_list_full:
        #     return
        if len(aosp_list) == 1 and len(extensive_list) == 1:
            self.entity_mapping(self.aosp_entities[aosp_list[0]], entity)
            return
        elif len(aosp_list) == len(extensive_list) and len(extensive_list) > 0:
            for aosp_ent, extensive_ent in zip(aosp_list, extensive_list):
                self.entity_mapping(self.aosp_entities[aosp_ent], self.extensive_entities[extensive_ent])
            return
        else:
            # 匿名类  todo 匿名类匹配顺位
            if entity.category == Constant.E_class and entity.name == Constant.anonymous_class:
                # 子匹配分轮次 第一轮，type bind hash
                for aosp_id in aosp_list:
                    for ext_id in extensive_list:
                        aosp_ent = self.aosp_entities[aosp_id]
                        ext_ent = self.extensive_entities[ext_id]
                        aosp_bind = self.aosp_entities[aosp_ent.anonymous]
                        ext_bind = self.extensive_entities[ext_ent.anonymous]
                        if aosp_ent.raw_type == ext_ent.raw_type and \
                                aosp_ent.entity_mapping == -1 and ext_ent.entity_mapping == -1:
                            if aosp_bind.id == ext_bind.entity_mapping and aosp_ent.total_hash == ext_ent.total_hash:
                                self.entity_mapping(aosp_ent, ext_ent)
                aosp_list: List[int] = [ent for ent in aosp_list_full if self.aosp_entities[ent].entity_mapping == -1]
                extensive_list: List[int] = [ent for ent in extensive_list_full if
                                             self.extensive_entities[ent].entity_mapping == -1]
                # 第二轮 type bind_name
                for aosp_id in aosp_list:
                    for ext_id in extensive_list:
                        aosp_ent = self.aosp_entities[aosp_id]
                        ext_ent = self.extensive_entities[ext_id]
                        aosp_bind = self.aosp_entities[aosp_ent.anonymous]
                        ext_bind = self.extensive_entities[ext_ent.anonymous]
                        if aosp_ent.raw_type == ext_ent.raw_type and \
                                aosp_ent.entity_mapping == -1 and ext_ent.entity_mapping == -1:
                            if aosp_bind.id == ext_bind.entity_mapping:
                                self.entity_mapping(aosp_ent, ext_ent)
                aosp_list: List[int] = [ent for ent in aosp_list_full if self.aosp_entities[ent].entity_mapping == -1]
                extensive_list: List[int] = [ent for ent in extensive_list_full if
                                             self.extensive_entities[ent].entity_mapping == -1]
                # 第三轮 type bind_name
                for aosp_id in aosp_list:
                    for ext_id in extensive_list:
                        aosp_ent = self.aosp_entities[aosp_id]
                        ext_ent = self.extensive_entities[ext_id]
                        aosp_bind = self.aosp_entities[aosp_ent.anonymous]
                        ext_bind = self.extensive_entities[ext_ent.anonymous]
                        if aosp_ent.raw_type == ext_ent.raw_type and \
                                aosp_ent.entity_mapping == -1 and ext_ent.entity_mapping == -1:
                            if aosp_bind.name == ext_bind.name:
                                self.entity_mapping(aosp_ent, ext_ent)
                aosp_list: List[int] = [ent for ent in aosp_list_full if self.aosp_entities[ent].entity_mapping == -1]
                extensive_list: List[int] = [ent for ent in extensive_list_full if
                                             self.extensive_entities[ent].entity_mapping == -1]
                # 第四轮 type
                for aosp_id in aosp_list:
                    for ext_id in extensive_list:
                        aosp_ent = self.aosp_entities[aosp_id]
                        ext_ent = self.extensive_entities[ext_id]
                        if aosp_ent.raw_type == ext_ent.raw_type and \
                                aosp_ent.entity_mapping == -1 and ext_ent.entity_mapping == -1:
                            self.entity_mapping(aosp_ent, ext_ent)
            # 类或接口或注解或枚举
            elif entity.category in [Constant.E_class, Constant.E_interface, Constant.E_enum, Constant.E_annotation]:
                for item_id in aosp_list:
                    if self.aosp_entities[item_id].abstract == entity.abstract:
                        # 外部类
                        if get_parent_entity(entity.id, self.extensive_entities).above_file_level():
                            self.entity_mapping(self.aosp_entities[item_id], entity)
                        else:
                            # 内部类
                            if self.parent_are_mapping(self.aosp_entities[item_id], entity):
                                self.entity_mapping(self.aosp_entities[item_id], entity)

            # 匿名类子实体
            elif Constant.anonymous_class in entity.qualifiedName:
                map_parent_anonymous_class = get_parent_anonymous_class(entity.id,
                                                                        self.extensive_entities).entity_mapping
                for item_id in aosp_list:
                    aosp_parent_anonymous_class = get_parent_anonymous_class(item_id,
                                                                             self.aosp_entities).id
                    if aosp_parent_anonymous_class == map_parent_anonymous_class:
                        self.entity_mapping(self.aosp_entities[item_id], entity)
                        break
            # 方法额外比较参数
            elif entity.category == Constant.E_method:
                for item_id in aosp_list_full:
                    if self.aosp_entities[item_id].parameter_names == search_param:
                        if item_id in aosp_list:
                            self.entity_mapping(self.aosp_entities[item_id], entity)
                        else:
                            self.entity_mapping_extract(self.aosp_entities[item_id], entity)
                        # if self.aosp_entities[item_id].parameter_names == search_param or \
                        #         (not (entity.not_aosp == 0 and entity.is_intrusive == 0) or
                        #          (self.aosp_entities[item_id].parameter_types == entity.parameter_types)):
                        #     self.entity_mapping(self.aosp_entities[item_id], entity)
                        return
            elif entity.category == Constant.E_variable:
                # 成员变量
                if get_parent_entity(entity.id, self.extensive_entities).category in [Constant.E_class,
                                                                                      Constant.E_interface]:
                    if len(aosp_list) > 0:
                        self.entity_mapping(self.aosp_entities[aosp_list[0]], entity)
                        return
                # 参数
                elif entity.is_param != -1:
                    # 参数结合 父实体方法的参数个数等，结构化信息匹配
                    extensive_parent_ent = get_parent_entity(entity.id, self.extensive_entities)
                    if extensive_parent_ent.entity_mapping > 0:
                        aosp_parent_ent = self.aosp_entities[extensive_parent_ent.entity_mapping]
                        # 基于匹配方法对检测
                        if aosp_parent_ent.entity_mapping == extensive_parent_ent.id:
                            aosp_child_params = aosp_parent_ent.parameter_entities
                            extensive_child_params = extensive_parent_ent.parameter_entities
                            if len(aosp_child_params) == len(extensive_child_params):
                                for aosp_param, extensive_param in zip(aosp_child_params, extensive_child_params):
                                    self.entity_mapping(self.aosp_entities[aosp_param],
                                                        self.extensive_entities[extensive_param])
                                return
                            else:
                                for aosp_param in aosp_child_params:
                                    if self.aosp_entities[aosp_param].name == entity.name:
                                        self.entity_mapping(self.aosp_entities[aosp_param],
                                                            entity)
                                        return
                        # 方法匹配，但伴生方法为方法提取，其中参数直接标记为伴生
                        else:
                            entity.set_honor(1)
                            try:
                                self.extensive_entities_um.pop(entity.id)
                            except KeyError:
                                pass
                            return
                # 局部变量
                else:
                    for ent in aosp_list:
                        # 同一方法内部
                        if get_parent_entity(entity.id, self.extensive_entities).entity_mapping > 0 and \
                                get_parent_entity(ent, self.aosp_entities).entity_mapping == entity.parentId and \
                                self.aosp_entities[ent].raw_type.rsplit('.')[-1] == entity.raw_type.rsplit('.')[-1] and \
                                self.aosp_entities[ent].name == entity.name:
                            self.entity_mapping(self.aosp_entities[ent], entity)
                            return
                            # 提取方法内部
                        elif entity.parentId in [get_parent_entity(ent, self.aosp_entities).extract_to] and \
                                self.aosp_entities[ent].raw_type.rsplit('.')[-1] == entity.raw_type.rsplit('.')[-1] and \
                                self.aosp_entities[ent].name == entity.name:
                            self.entity_mapping(self.aosp_entities[ent], entity)
                            return
            else:
                for ent in aosp_list:
                    if self.aosp_entities[ent].name == entity.name:
                        self.entity_mapping(self.aosp_entities[ent], entity)
                        return
                return
            return -1

    def struct_match(self, entity: Entity):
        left_neighbor = self.get_neighbor_entity(entity, self.extensive_entities, entity.category, 'left')
        right_neighbor = self.get_neighbor_entity(entity, self.extensive_entities, entity.category, 'right')
        left_neighbor_mapping = self.get_entity_mapping(left_neighbor, 1)
        right_neighbor_mapping = self.get_entity_mapping(right_neighbor, 1)
        if entity.category == Constant.E_method:
            # 可能的重命名
            if left_neighbor_mapping > 0 and \
                    self.get_neighbor_entity(
                        self.aosp_entities[left_neighbor_mapping],
                        self.aosp_entities,
                        self.aosp_entities[left_neighbor_mapping].category,
                        'right'
                    ) in self.aosp_entities_um.keys():
                possible_match_ent = self.aosp_entities[
                    self.get_neighbor_entity(
                        self.aosp_entities[left_neighbor_mapping],
                        self.aosp_entities,
                        self.aosp_entities[left_neighbor_mapping].category,
                        'right'
                    )
                ]
                # 被夹逼的方法
                if right_neighbor_mapping > 0 and right_neighbor_mapping == self.get_neighbor_entity(
                        possible_match_ent,
                        self.aosp_entities,
                        possible_match_ent.category,
                        'right'
                ):
                    self.children_match(entity, possible_match_ent.qualifiedName, possible_match_ent.parameter_names,
                                        possible_match_ent.file_path)
                else:
                    # 拥有共同参数
                    possible_match_ent_params = [self.aosp_entities[param].name for param in
                                                 possible_match_ent.parameter_entities]
                    entity_params = [self.extensive_entities[param].name for param in entity.parameter_entities]
                    if len(set(possible_match_ent_params) & set(entity_params)) > 0 or \
                            len(possible_match_ent.parameter_entities) == len(entity.parameter_entities):
                        self.children_match(entity, possible_match_ent.qualifiedName,
                                            possible_match_ent.parameter_names,
                                            possible_match_ent.file_path)

            elif left_neighbor in entity.called_entities and left_neighbor_mapping > 0:
                left_neighbor_ent = self.aosp_entities[left_neighbor_mapping]
                if left_neighbor_ent.name == entity.name:
                    self.children_match(entity, left_neighbor_ent.qualifiedName, left_neighbor_ent.parameter_names,
                                        left_neighbor_ent.file_path)
            elif right_neighbor in entity.called_entities and right_neighbor_mapping > 0:
                right_neighbor_ent = self.aosp_entities[right_neighbor_mapping]
                if right_neighbor_ent.name == entity.name:
                    self.children_match(entity, right_neighbor_ent.qualifiedName, right_neighbor_ent.parameter_names,
                                        right_neighbor_ent.file_path)
        elif entity.category == Constant.E_variable:
            pass

    def refactor_match(self, entity: Entity, ent_refactor_info: list):
        move_list = set()
        for move in ent_refactor_info:
            move_type: str = move[0]
            source_state: BaseState = move[1]

            entity.set_refactor(
                {'type': move_type, 'source_name': source_state.longname(),
                 'source_param': source_state.get_param()})

            move_list.add(move_type)
            if move_type in MoveClassRefactoring.keys():
                entity.set_honor(0)
                entity.set_intrusive(1)
                self.children_match(entity, source_state.longname(), source_state.get_param(), source_state.file_path)
                for move_name in MoveClassRefactoring[move_type]:
                    entity.set_intrusive_modify(move_name, '-')
            elif move_type in MoveMethodRefactorings.keys():
                entity.set_honor(0)
                entity.set_intrusive(1)
                self.children_match(entity, source_state.longname(), source_state.get_param(), source_state.file_path)
                for move_name in MoveMethodRefactorings[move_type]:
                    entity.set_intrusive_modify(move_name, '-')
            elif move_type in ExtractMethodRefactorings.keys():
                entity.set_honor(1)
                entity.set_intrusive(1)
                # for ent in child_param[ent.id]:
                #     ent.set_honor(1)
                self.children_match(entity, source_state.longname(), source_state.get_param(), source_state.file_path)
                for move_name in ExtractMethodRefactorings[move_type]:
                    entity.set_intrusive_modify(move_name, '-')
            elif move_type in MoveMethodParamRefactorings.keys():
                if entity.category == Constant.E_method:
                    entity.set_honor(0)
                    entity.set_intrusive(1)
                    self.children_match(entity, source_state.longname(), source_state.get_param(),
                                        source_state.file_path)
                    for move_name in MoveMethodParamRefactorings[move_type]:
                        entity.set_intrusive_modify(move_name, '-')
                elif entity.category == Constant.E_variable:
                    if move_type == "Rename Parameter":
                        entity.set_honor(0)
                        entity.set_intrusive(1)
                        entity.set_intrusive_modify("rename", '-')
                    elif move_type == "Add Parameter":
                        entity.set_honor(1)

    def children_match(self, entity, search_name: str, search_param: str, search_file: str):
        self.exactly_match(entity, search_name, search_param, search_file)
        for child_param in entity.parameter_entities:
            child_param_ent = self.extensive_entities[child_param]
            self.children_match(child_param_ent,
                                f"{search_name}.{child_param_ent.name}",
                                child_param_ent.parameter_names,
                                search_file)
        for child in entity.children:
            child_ent = self.extensive_entities[child]
            self.children_match(child_ent,
                                f"{search_name}.{child_ent.name}",
                                child_ent.parameter_names,
                                search_file)

    def start_mapping(self, refactor_list: Dict[int, list]):
        # 第一轮
        for entity in self.extensive_entities:
            if entity.id in self.extensive_entities_um.keys():
                self.exactly_match(entity, entity.qualifiedName, entity.parameter_names, entity.file_path)

        # 第二轮
        current_unmatch_entities = self.extensive_entities_um.copy()
        for entID, entity in current_unmatch_entities.copy().items():
            if entID in self.extensive_entities_um.keys():
                self.struct_match(entity)

        # 第三轮
        current_unmatch_entities = self.extensive_entities_um.copy()
        for entID, entity in current_unmatch_entities.copy().items():
            if entID in refactor_list.keys() and entID in self.extensive_entities_um.keys():
                self.refactor_match(entity, refactor_list[entID][1])

    def entity_mapping(self, aosp_entity: Entity, extensive_entity: Entity):
        aosp_entity.set_entity_mapping(extensive_entity.id)
        extensive_entity.set_entity_mapping(aosp_entity.id)
        try:
            self.aosp_entities_um.pop(aosp_entity.id)
            self.extensive_entities_um.pop(extensive_entity.id)
        except Exception:
            pass

    def entity_mapping_extract(self, aosp_entity: Entity, extensive_entity: Entity):
        aosp_entity.set_extract_to(extensive_entity.id)
        extensive_entity.set_entity_mapping(aosp_entity.id)
        try:
            self.extensive_entities_um.pop(extensive_entity.id)
        except Exception:
            pass
        try:
            self.extensive_entities_um.pop(extensive_entity.id)
        except Exception:
            pass

    def parent_are_mapping(self, aosp_entity: Entity, extensive_entity: Entity):
        if get_parent_entity(extensive_entity.id, self.extensive_entities).entity_mapping > 0 and \
                get_parent_entity(aosp_entity.id, self.aosp_entities).entity_mapping == extensive_entity.parentId:
            return True
        return False

    def get_ownership(self, chang_files: List[str], all_entities: dict, all_native_entities: dict,
                      old_native_entities: dict, old_update_entities: dict, intrusive_entities: dict,
                      old_intrusive_entities: dict, pure_accompany_entities: dict):
        keys_all_entities = all_entities.keys()
        keys_intrusive_entities = intrusive_entities.keys()
        keys_old_intrusive_entities = old_intrusive_entities.keys()
        keys_pure_accompany_entities = pure_accompany_entities.keys()
        keys_old_native_entities = old_native_entities.keys()
        keys_old_update_entities = old_update_entities.keys()
        keys_all_native_entities = all_native_entities.keys()
        for entity in self.extensive_entities:
            if not entity.above_file_level() and entity.not_aosp == -2:
                if entity.entity_mapping >= 0:
                    if entity.id in keys_old_native_entities or entity.id in keys_old_update_entities:
                        entity.set_honor(0)
                        entity.set_old_aosp(1)
                    elif entity.id in keys_old_intrusive_entities:
                        entity.set_honor(0)
                        entity.set_old_aosp(1)
                        entity.set_intrusive(1)
                    elif entity.id in keys_all_native_entities:
                        entity.set_honor(0)
                    else:
                        entity.set_honor(0)
                        entity.set_intrusive(1)
                else:
                    if entity.id in keys_old_native_entities or entity.id in keys_old_update_entities:
                        entity.set_honor(0)
                        entity.set_old_aosp(1)
                    elif entity.id in keys_old_intrusive_entities:
                        entity.set_honor(0)
                        entity.set_old_aosp(1)
                        entity.set_intrusive(1)
                    elif entity.id in keys_all_native_entities:
                        entity.set_honor(0)
                    else:
                        entity.set_honor(1)

    def get_ownership_by_body(self, chang_files: List[str]):
        for entity in self.extensive_entities:
            if (not entity.above_file_level()) and entity.not_aosp == -2:
                if entity.file_path in chang_files:
                    if entity.entity_mapping >= 0:
                        entity.set_honor(0)
                        if entity.category == Constant.E_class:
                            if get_parent_entity(entity.id, self.extensive_entities).category == Constant.E_file:
                                entity.set_intrusive(1)
                            else:
                                change = 0 if entity.total_hash == self.aosp_entities[entity.entity_mapping].total_hash \
                                    else 1
                                entity.set_intrusive(change)
                        elif entity.category == Constant.E_method:
                            if entity.id in self.aosp_entities[entity.entity_mapping].extract_to:
                                entity.set_honor(1)
                                entity.set_intrusive(1)
                            else:
                                change = 0 if entity.total_hash == self.aosp_entities[entity.entity_mapping].total_hash \
                                    else 1
                                entity.set_intrusive(change)
                        elif entity.category == Constant.E_variable:
                            change = 0 if entity.total_hash == self.aosp_entities[entity.entity_mapping].total_hash \
                                else 1
                            # 当前enre输出变量位置，参数包含整体，其余变量位置从变量名第一字符开始，故在此做特殊处理
                            if entity.is_param != -1:
                                entity.set_intrusive(change)
                            else:
                                if entity.modifiers == self.aosp_entities[entity.entity_mapping].modifiers and \
                                        entity.annotations == self.aosp_entities[entity.entity_mapping].annotations and \
                                        entity.raw_type.rsplit('.', 1)[-1] == \
                                        self.aosp_entities[entity.entity_mapping].raw_type.rsplit('.', 1)[-1]:
                                    entity.set_intrusive(change)
                                else:
                                    entity.set_intrusive(1)
                        else:
                            change = 0 if entity.total_hash == self.aosp_entities[entity.entity_mapping].total_hash \
                                else 1
                            entity.set_intrusive(change)
                    else:
                        entity.set_honor(1)
                else:
                    entity.set_honor(0)

    def run_mapping_and_ownership(self, refactor_list, chang_files):
        self.start_mapping(refactor_list)
        self.get_ownership_by_body(chang_files)

    def get_neighbor_entity(self, entity: Entity, entities: List[Entity], category: str, direction: str):
        # 寻找邻居实体时，要求实体类型，父实体一致
        if direction == 'left':
            left_ent_id = entity.id - 1
            while left_ent_id >= 0 and entities[left_ent_id].category != category:
                left_ent_id -= 1
            return left_ent_id if (left_ent_id >= 0 and entities[left_ent_id].parentId == entity.parentId) else -1
        else:
            child_entities = list(entity.parameter_entities + list(entity.children))
            child_entities.sort()
            right_ent_id = entity.id + 1 if entity.id + 1 not in child_entities else child_entities[-1] + 1
            while right_ent_id < len(entities) and entities[right_ent_id].category != category:
                right_ent_id += 1
            return right_ent_id if (
                    right_ent_id < len(entities) and
                    entities[right_ent_id].parentId == entity.parentId
            ) else -1

    def get_entity_mapping(self, entity_id: int, direction: int):
        if entity_id < 0:
            return -1
        return self.extensive_entities[entity_id].entity_mapping if direction == 1 else \
            self.aosp_entities[entity_id].entity_mapping


def get_parent_entity(entity: int, entity_set: List[Entity]):
    return entity_set[entity_set[entity].parentId]


# get parent Anonymous_class
def get_parent_anonymous_class(entity: int, entity_set: List[Entity]):
    temp = entity
    while entity_set[temp].name != Constant.anonymous_class and entity_set[temp].parentId >= 0:
        temp = get_parent_entity(temp, entity_set).id
        print("\r", end="")
        print('parent', temp, end="")
    return entity_set[temp] if temp > -1 else None

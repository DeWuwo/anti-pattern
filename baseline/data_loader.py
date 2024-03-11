import json
import os

from typing import List

from model.dependency.entity import Entity
from constant.constant import Constant
from baseline.code_tracker import CodeTracker


class DataLoader:
    data_set_file_list: list
    set_entities: List[Entity]
    data_set_entities: List[Entity]

    def __init__(self):
        self.source_code_path = 'D:\\Honor\\source_code\\'
        self.source_dep_path = 'D:\\Honor\\dep_res\\'
        self.out_path = 'E:\\Graduate\\baseline\\'
        self.data_set_file_list = ['services/core/java/com/android/server/pm/PackageManagerService.java',
                                   'services/core/java/com/android/server/am/ActivityManagerService.java',
                                   'services/core/java/com/android/server/wm/WindowManagerService.java',
                                   'packages/SystemUI/src/com/android/systemui/statusbar/phone/StatusBar.java']
        self.set_entities: List[Entity] = []
        self.data_set_entities: List[Entity] = []
        self.data_set_project = [
            ['aospa', 'sapphire', 'base', '15d9159eb00fb7fd92f9dc249af588f655fd8f66',
             '898ad0236f79d81514806e4f4ca3a2fe401e0705', 'null', 'null', 'android-12'],
            ['OmniROM', 'android-11', 'base', 'a362a5abfe0dbcf48877c5b02d1a8da8d9c504c6',
             'ba595d5debf2a214e05a8a774be658b09b354d1a', 'null', 'null', 'android-11'],
            ['LineageOS', 'lineage-18.1', 'base', '7f7fc2562a95be630dbe609e8fb70383dcfada4f',
             '49d8b986dddd441df741698541788c5f3a9c465f', 'hiddenapi-flags-lineage18.csv', 'hiddenapi-flags-11.csv',
             'android-11'],
        ]

    def get_path(self, ext_name: str, ext_version: str, pkg: str, ext_commit, aosp_commit: str, os_hidden: str,
                 aosp_hidden, aosp_base_version: str):
        repo_path = os.path.join(self.source_code_path, ext_name, pkg)
        dep_path = os.path.join(self.source_dep_path, ext_name, pkg, ext_commit + '.json')
        out_path = os.path.join(self.out_path, ext_name)
        return repo_path, aosp_commit, ext_commit, out_path, dep_path

    def run_code_tracker_by_proj(self):
        for proj in self.data_set_project:
            repo_path, aosp_commit, ext_commit, out_path, dep_path = self.get_path(*proj)
            CodeTracker().run(repo_path, aosp_commit, ext_commit, dep_path, ",".join(self.data_set_file_list), out_path)

    # 加载单个项目实体依赖
    def load_entities(self, file_path: str):
        print("load entities")
        with open(file_path, encoding='utf-8') as h:
            honor = json.load(h, strict=False)
            entities = honor['variables']
            for entity_info in entities:
                if not entity_info['external']:
                    entity = Entity(**entity_info)
                    self.set_entities.append(entity)
                    if entity.file_path in self.data_set_file_list:
                        self.data_set_entities.append(entity)
        return self.set_entities, self.data_set_entities

    def run_code_tracker(self):
        for proj in self.data_set_project:
            repo_path, aosp_commit, ext_commit, out_path, dep_path = self.get_path(*proj)
            self.load_entities(dep_path)
            print('run code tracker')
            for ent in self.data_set_entities:
                print(f'detect entity {ent.id}', end="")
                parentName = "null"
                parentStartLine = -1
                if ent.category == Constant.E_variable and self.set_entities[
                    ent.parentId].category == Constant.E_method:
                    parentName = self.set_entities[ent.parentId].name
                    parentStartLine = self.set_entities[ent.parentId].start_line
                category = ent.category
                if ent.category == Constant.E_variable and self.set_entities[ent.parentId].category == Constant.E_class:
                    category = "Attribute"
                CodeTracker().run(repo_path, aosp_commit, ext_commit, dep_path, "".join(self.data_set_file_list),
                                  out_path)

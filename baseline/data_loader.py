import json
import os

from typing import List, Dict

from model.dependency.entity import Entity
from constant.constant import Constant
from baseline.code_tracker import CodeTracker
from utils import FileCSV


class DataStruct:
    id: int
    name: str
    category: str
    ownership: str
    file_path: str
    change_type: set

    def __init__(self, ent_id, ent_name, ent_category, ent_ownership, file_path, ent_change_types):
        self.id = ent_id
        self.name = ent_name
        self.category = ent_category
        self.ownership = ent_ownership
        self.file_path = file_path
        self.change_type = ent_change_types


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
        self.change_type = {
            "access_modify": "access_modify",
            "final_modify": "modifier_modify",
            "static_modify": "modifier_modify",
            "global_modify": "modifier_modify",
            "body_modify": "body_modify",
            "rename": "rename",
            "move": "move",
            "extracted": "extracted",
            "type_modify": "type_modify",
            "annotation_modify": "annotation_modify",
            "param_modify": "param_modify",
            "return_type_modify": "return_type_modify",
            "Extract Method": 'extracted',
            "parent_interface_modify": "",
            "parent_class_modify": "",
        }
        self.ground_truth_source: Dict[int, DataStruct] = {}
        self.ground_truth_ownership = {}
        self.ground_truth_change_type = {}
        for file in self.data_set_file_list:
            self.ground_truth_ownership[file] = {"actively native": [], "intrusive native": [], "extensive": []}
        for category in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute", "Other"]:
            self.ground_truth_change_type[category] = {"actively native": [], "intrusive native": [], "extensive": []}

    # 加载数据集实体依赖
    def load_entity(self, ent: dict):

        ent_id = int(ent["id"])
        ent_name = ent["qualifiedName"]
        ent_category = ent["category"]
        ent_ownership = ent["ownership"]
        ent_modify = ent["modify"]
        ent_change_types = set()
        for k in eval(ent_modify).keys():
            if self.get_modify_type(k) != "":
                ent_change_types.add(self.get_modify_type(k))
        ent_category = self.get_entity_category(ent_name, ent_category)
        if ent_modify == "{}":
            if "native" in ent_ownership and "intrusive" not in ent_ownership:
                ent_ownership = "actively native"
        return ent_id, ent_name, ent_category, ent_ownership, ent_change_types

    def get_entity_category(self, ent_name: str, string: str):
        if string == Constant.E_class and ent_name.endswith(Constant.anonymous_class):
            return "Other"
        if string == Constant.E_variable:
            ent_name_list = ent_name.split(".")
            if str(ent_name_list[-2][0]).isupper() and ent_name_list[-2] != ent_name_list[-3] and ent_name_list[
                -2] != Constant.anonymous_class:
                return "Attribute"
        return string if string in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute"] else "Other"

    def load_ground_truth_source(self, file_path: str):
        print("load entities")
        entities = FileCSV.read_dict_from_csv(file_path)
        # 初始化
        self.ground_truth_source: Dict[int, DataStruct] = {}
        self.ground_truth_ownership = {}
        self.ground_truth_change_type = {}
        for file in self.data_set_file_list:
            self.ground_truth_ownership[file] = {"actively native": [], "intrusive native": [], "extensive": []}
        for category in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute", "Other"]:
            self.ground_truth_change_type[category] = {"actively native": [], "intrusive native": [], "extensive": []}
        for ent in entities:
            ent_file = ent["file_path"]
            if ent_file in self.data_set_file_list:
                ent_id, ent_name, ent_category, ent_ownership, ent_change_types = self.load_entity(ent)
                # if ent_category in ent_category in [Constant.E_class, Constant.E_method, Constant.E_variable,
                #                                     "Attribute"] and \
                #         not str(ent_name).endswith(Constant.anonymous_class):
                ent_type = DataStruct(ent_id, ent_name, ent_category, ent_ownership, ent_file, ent_change_types)
                self.ground_truth_source[ent_id] = ent_type
                self.ground_truth_ownership[ent_file][ent_type.ownership].append(ent_type.id)
                self.ground_truth_change_type[ent_category][ent_type.ownership].append(ent_type.id)

    def get_target_data_style(self, file_path: str):

        self.load_ground_truth_source(file_path)
        ownership = []
        change = []
        for file, datas in self.ground_truth_ownership.items():
            file_data = {"file_path": file, "total": 0}
            for owner, ents in datas.items():
                file_data["total"] += len(ents)
                file_data.update({owner: len(ents)})
            ownership.append(file_data)
        for category, datas in self.ground_truth_change_type.items():
            file_data = {"category": category, "total": 0}
            for owner, ents in datas.items():
                file_data["total"] += len(ents)
                file_data.update({owner: len(ents)})
            change.append(file_data)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", "ground_truth_o", ownership, "a",
                                  False)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", "ground_truth_c", change, "a",
                                  False)

    def load_our_method(self, file_path: str):
        print("load out method")
        entities = FileCSV.read_dict_from_csv(file_path)
        res = []
        for ent in entities:
            ent_file = ent["file_path"]
            if ent_file in self.data_set_file_list:
                ent_id, ent_name, ent_category, ent_ownership, ent_change_types = self.load_entity(ent)
                # if ent_category in ent_category in [Constant.E_class, Constant.E_method, Constant.E_variable,
                #                                     "Attribute"] and \
                #         not str(ent_name).endswith(Constant.anonymous_class):
                res.append([ent_id, ent_ownership, ent_change_types])
        return res

    def compare_change_type(self, change_set1: set, change_set2: set):
        if len(change_set1 & change_set2) == len(change_set1) and len(change_set1) == len(change_set2):
            return True
        diff12 = change_set1 - change_set2
        diff21 = change_set2 - change_set1
        if len(diff12) == 0 and len(diff21) == 1 and "body_modify" in diff21:
            return True
        if len(diff21) == 0 and len(diff12) == 1 and "body_modify" in diff12:
            return True
        return False

    def compare(self, file_path, method):
        print("compare", method, "----------------")
        if method == "codeTracker":
            res = CodeTracker().load_res(f"{file_path}/{method}.csv")
        elif method == "our":
            res = self.load_our_method(f"{file_path}/{method}.csv")
        else:
            res = []
        res_total = {}
        res_ownership_correct = {}
        res_change_type_correct = {}
        for category in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute", "Other"]:
            res_total[category] = {"actively native": [], "intrusive native": [], "extensive": []}
            res_ownership_correct[category] = {"actively native": [], "intrusive native": [], "extensive": []}
            res_change_type_correct[category] = {"actively native": [], "intrusive native": [],
                                                 "extensive": []}
        for data in res:
            base_ent = self.ground_truth_source[data[0]]
            category = base_ent.category
            base_ownership = base_ent.ownership
            base_changes = base_ent.change_type
            file = base_ent.file_path
            if file in self.data_set_file_list:
                method_ownership = data[1]
                # 如果不检测class body 或者 变量 body，特殊处理
                if method_ownership == "actively native" and base_ownership == "intrusive native" and \
                        category in ["Class", "Variable", "Attribute"] and "body_modify" in base_changes and len(
                    base_changes) == 1:
                    method_ownership = "intrusive native"
                res_total[category][method_ownership].append(data[0])
                if method_ownership == base_ownership:
                    res_ownership_correct[category][method_ownership].append(data[0])
                    if base_ownership != "actively native":
                        if self.compare_change_type(data[2], base_changes):
                            res_change_type_correct[category][base_ownership].append(data[0])
        source = []
        ownership = []
        change = []
        for category, datas in res_total.items():
            file_data = {"category": category, "total": 0}
            for owner, ents in datas.items():
                file_data["total"] += len(ents)
                file_data.update({owner: len(ents)})
            source.append(file_data)
        for category, datas in res_ownership_correct.items():
            file_data = {"category": category, "total": 0}
            for owner, ents in datas.items():
                file_data["total"] += len(ents)
                file_data.update({owner: len(ents)})
            ownership.append(file_data)
        for category, datas in res_change_type_correct.items():
            file_data = {"category": category, "total": 0}
            for owner, ents in datas.items():
                file_data["total"] += len(ents)
                file_data.update({owner: len(ents)})
            change.append(file_data)
        # 归属放准确率
        code_tracker_ownership_correct_yz = []
        for category in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute", "Other"]:
            res = {"category": category}
            for own in ["actively native", "intrusive native", "extensive"]:

                change_method = len(res_total[category][own])
                change_method_corr = len(res_ownership_correct[category][own])
                change_base = len(self.ground_truth_change_type[category][own])
                print("多了", category, own, "-",
                      set(res_total[category][own]) - set(self.ground_truth_change_type[category][own]))
                print("漏了", category, own, "-",
                      set(self.ground_truth_change_type[category][own]) - set(res_total[category][own]))
                try:
                    res.update({f"{own}_c": change_method_corr / change_method,
                                f"{own}_z": change_method_corr / change_base})
                except Exception:
                    res.update({f"{own}_c": 0,
                                f"{own}_z": 0})
            code_tracker_ownership_correct_yz.append(res)
        # 变更准确率
        code_tracker_change_type_correct_yz = []
        for category in [Constant.E_class, Constant.E_method, Constant.E_variable, "Attribute", "Other"]:
            change_method = len(res_total[category]["intrusive native"]) + \
                            len(res_total[category]["extensive"])
            change_method_corr = len(res_change_type_correct[category]["intrusive native"]) + \
                                 len(res_change_type_correct[category]["extensive"])
            change_base = len(self.ground_truth_change_type[category]["intrusive native"]) + \
                          len(self.ground_truth_change_type[category]["extensive"])
            print("漏了", category, "-",
                  set(self.ground_truth_change_type[category]["intrusive native"] +
                      self.ground_truth_change_type[category]["extensive"]) - set(
                      res_change_type_correct[category]["intrusive native"] + res_change_type_correct[category][
                          "extensive"])
                  )
            try:
                code_tracker_change_type_correct_yz.append(
                    {"category": category, "c": change_method_corr / change_method,
                     "z": change_method_corr / change_base})
            except Exception:
                code_tracker_change_type_correct_yz.append({"category": category, "c": 0, "z": 0})

        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", f"{method}_s", source, 'a', False)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", f"{method}_o", ownership, "a",
                                  False)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", f"{method}_c", change, "a", False)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", f"{method}_owner",
                                  code_tracker_ownership_correct_yz, "a", False)
        FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\ground_truth\\code_diff", f"{method}_change",
                                  code_tracker_change_type_correct_yz, "a", False)

    def get_modify_type(self, string: str):
        if "body_modify" in string:
            return "body_modify"
        elif string not in self.change_type.keys():
            return ""
        return self.change_type[string]

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


if __name__ == '__main__':
    ground_truth = [
        "E:\\Graduate\\baseline\\ground_truth\\code_diff\\aospa",
        "E:\\Graduate\\baseline\\ground_truth\\code_diff\\OmniROM"
    ]
    for proj in ground_truth:
        data_loader = DataLoader()
        data_loader.get_target_data_style(f"{proj}\\base.csv")
        data_loader.compare(proj, "codeTracker")
        data_loader.compare(proj, "our")

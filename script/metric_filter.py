from typing import List

from utils import FileJson, FileCSV


class MetricFilter:
    file_path: str
    out_path: str

    def __init__(self, file_path: str, out_path: str):
        self.file_path = file_path
        self.out_path = out_path

    def load_total_anti_patterns(self):
        res: dict = FileJson.read_base_json(self.file_path)['res']['values']
        return res

    def load_metric_anti_patterns(self):
        dict_res = {}
        res = FileJson.read_base_json(self.file_path)['res']
        for item in res:
            dict_res.update(item)
        return dict_res

    def handle_load_divide_mc(self, patterns: List[str], styles: List[str], proj: str):
        res = self.load_total_anti_patterns()
        mc_res = {"project": proj, "major": set(), "minor": set()}
        for pattern in patterns:
            method = getattr(self, f'handle_count_mc_{pattern}', None)
            style_res = method(res[pattern], styles)
            mc_res.update(style_res)
            for key, val in style_res.items():
                if "major" in key:
                    mc_res["major"] = mc_res["major"] | val
                else:
                    mc_res["minor"] = mc_res["minor"] | val

        FileCSV.write_dict_to_csv(self.out_path, "pattern_divide_mc", [mc_res], 'a', False)

    def handle_count(self, patterns: List[str], proj: str):
        res = self.load_metric_anti_patterns()
        count_res = {"project": proj}
        for pattern in patterns:
            method = getattr(self, f'handle_count_{pattern}', None)
            count_res.update(method(res[pattern]))

        FileCSV.write_dict_to_csv(self.out_path, "metric_count", [count_res], 'a', False)

    def handle_count_FinalDel(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if "res" in val.keys():
                if "is_inherit" in val['res'].keys():
                    metric = val['res']["is_inherit"]
                    try:
                        res.update({
                            f"{key}_is_inherit": metric['is_inherit'],
                            f"{key}_no_inherit": metric['no_inherit']
                        })
                    except Exception:
                        res.update({
                            f"{key}_is_inherit": 0,
                            f"{key}_no_inherit": 0
                        })
                elif "is_override" in val['res'].keys():
                    metric = val['res']["is_override"]
                    try:
                        res.update({
                            f"{key}_is_override": metric['is_override'],
                            f"{key}_no_override": metric['no_override']
                        })
                    except Exception:
                        res.update({
                            f"{key}_is_override": 0,
                            f"{key}_no_override": 0
                        })

                else:
                    res.update({})

        return res

    def handle_count_mc_FinalDel(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "is_inherit" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[len(mc["is_inherit"]) <= 0]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
                elif "is_override" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[len(mc["is_override"]) <= 0]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res

    def handle_count_AccessibilityModify(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            try:
                if val['res']:
                    metric = val['res']["native_used_effectiveness"]
                    useful = 0
                    useless = 0
                    for num, cou in metric.items():
                        if num == '0':
                            useless += cou
                        else:
                            useful += cou
                    res.update({
                        f"{key}_useful": useful,
                        f"{key}_useless": useless
                    })
                else:
                    res.update({
                        f"{key}_useful": 0,
                        f"{key}_useless": 0
                    })
            except KeyError:
                if val['res']:
                    metric = val['res']["native_used_frequency"]
                    useful = 0
                    useless = 0
                    for num, cou in metric.items():
                        if "e0" in num:
                            useless += cou
                        else:
                            useful += cou
                    res.update({
                        f"{key}_useful": useful,
                        f"{key}_useless": useless
                    })
                else:
                    res.update({
                        f"{key}_useful": 0,
                        f"{key}_useless": 0
                    })
        return res

    def handle_count_mc_AccessibilityModify(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "native_used_effectiveness" in mc.keys():
                    m = {True: "major", False: "minor"}
                    yx = sum([int(item) for _, item in mc["native_used_effectiveness"].items()])
                    try:
                        res[f'{key}_{m[yx <= 0]}'].add(mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res

    def handle_count_HiddenApi(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if val['res']:
                metric = val['res']["acceptable_hidden"]
                res.update({
                    f"{key}_all_acceptable": metric['all_acceptable_hidden'],
                    f"{key}_mix_acceptable": metric['mix_acceptable_hidden'],
                    f"{key}_no_acceptable": metric['no_acceptable_hidden']
                })
            else:
                res.update({
                    f"{key}_all_acceptable": 0,
                    f"{key}_mix_acceptable": 0,
                    f"{key}_no_acceptable": 0
                })
        return res

    def handle_count_mc_HiddenApi(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "acceptable_hidden" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[False in mc["acceptable_hidden"]]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res

    def handle_count_ParameterListModifyDep(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if val['res']:
                metric = val['res']["native_used_frequency"]
                res.update({
                    f"{key}_down": metric['n0_e1'] + metric['n1_e1'],
                    f"{key}_up": metric['n1_e0'],
                    f"{key}_no": metric['n0_e0']
                })
            else:
                res.update({
                    f"{key}_down": 0,
                    f"{key}_up": 0,
                    f"{key}_no": 0
                })
        return res

    def handle_count_mc_ParameterListModifyDep(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "native_used_frequency" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[int(mc["native_used_frequency"]["used_by_extension"]) <= 0]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res

    def handle_count_InheritExtension(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if val['res']:
                metric = val['res']["is_inherit"]
                res.update({
                    f"{key}_is_inherit": metric['is_inherit'],
                    f"{key}_no_inherit": metric['no_inherit']
                })
            else:
                res.update({
                    f"{key}_is_inherit": 0,
                    f"{key}_no_inherit": 0
                })
        return res

    def handle_count_mc_InheritExtension(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "is_inherit" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[len(mc["is_inherit"]) == 0]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res

    def handle_count_ImplementExtension(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if val['res']:
                metric = val['res']["is_new_implement"]
                res.update({
                    f"{key}_new_implement": metric['new_add_implement'],
                    f"{key}_modify_implement": metric['modify_implement']
                })
            else:
                res.update({
                    f"{key}_new_implement": 0,
                    f"{key}_modify_implement": 0
                })
        return res

    def handle_count_ReflectUse(self, pattern_info: dict):
        res = {}
        for key, val in pattern_info.items():
            if val['res']:
                metric = val['res']["open_in_sdk"]
                res.update({
                    f"{key}_all_not_in_sdk": metric['all_not_in_sdk'],
                    f"{key}_mix_in_sdk": metric['mix_in_sdk'],
                    f"{key}_all_in_sdk": metric['all_in_sdk']
                })
            else:
                res.update({
                    f"{key}_all_not_in_sdk": 0,
                    f"{key}_mix_in_sdk": 0,
                    f"{key}_all_in_sdk": 0
                })
        return res

    def handle_count_mc_ReflectUse(self, pattern_info: dict, styles):
        res = {}
        for key, val in pattern_info["res"].items():
            if key not in styles:
                continue
            res[f"{key}_major"] = set()
            res[f"{key}_minor"] = set()
            for exa in val["res"]:
                mc = exa["metrics"]
                if "open_in_sdk" in mc.keys():
                    m = {True: "major", False: "minor"}
                    try:
                        res[f'{key}_{m[len(mc["open_in_sdk"]["in_sdk"]) > 0]}'].add(
                            mc["stability"]["maintenance_cost"]["extensive"]["filename"])
                    except Exception:
                        pass
        return res


if __name__ == '__main__':
    patterns = ["FinalDel", "AccessibilityModify", "HiddenApi", "ParameterListModifyDep", "InheritExtension"
        , "ReflectUse"]
    styles = [
        'del_native_class_final', 'del_native_method_final',
        'native_class_access_modify', 'native_method_access_modify',
        'call_native_hidden_method', 'use_native_hidden_variable',
        'native_method_add_parameter',
        'native_class_inherit_extensive_class',
        'extensive_method_reflect_native_method', 'extensive_method_reflect_native_class']
    MetricFilter("E:/Graduate/datas/match_res_new/aospa/base/sapphire/anti-patterns/res.json", "E:\\test\\").handle_load_divide_mc(
        patterns, styles, "test")

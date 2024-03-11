from typing import List

from utils import FileJson, FileCSV


class MetricFilter:
    file_path: str
    out_path: str

    def __init__(self, file_path: str, out_path: str):
        self.file_path = file_path
        self.out_path = out_path

    def load_metric_anti_patterns(self):
        dict_res = {}
        res = FileJson.read_base_json(self.file_path)['res']
        for item in res:
            dict_res.update(item)
        return dict_res

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


if __name__ == '__main__':
    patterns = ["FinalDel", "AccessibilityModify", "HiddenApi", "ParameterListModifyDep", "InheritExtension",
                "ImplementExtension", "ReflectUse"]
    MetricFilter("E:\\数据\ground_truth\\aospa-sapphire\\res_metric_statistic.json", "E:\\数据\\metric\\").handle_count(
        patterns)

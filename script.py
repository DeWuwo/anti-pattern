import os

from script.script import Script
from script.intrusive import IntrusiveCompare
from script.facade_filter import FacadeFilter
from script.data_to_latex import ToLatex
from script.intrusive_type import IntrusiveType
from script.facade_top_file import FileTop
from script.intrusive_filter import IntrusiveFilter
from script.file_move import FileMove
from script.metric_filter import MetricFilter
from utils import FileCSV
from constant.constant import Constant

import sys
import time

if __name__ == '__main__':
    Script('E:\\Graduate\\RefactoringMine\\utils-3.0.2-modify\\bin').run_command()
    out_dir = 'D:\\Honor\\match_res_new'

    def get_out_path(out_path: str, tail_path=''):
        lineage = [
            ('lineage-16.0', f'{out_path}\\LineageOS\\base\\lineage-16.0\\{tail_path}'),
            ('lineage-17.1', f'{out_path}\\LineageOS\\base\\lineage-17.1\\{tail_path}'),
            ('lineage-18.1', f'{out_path}\\LineageOS\\base\\lineage-18.1\\{tail_path}'),
            ('lineage-19.1', f'{out_path}\\LineageOS\\base\\lineage-19.1\\{tail_path}'),
            ('lineage-20.0', f'{out_path}\\LineageOS\\base\\lineage-20.0\\{tail_path}')
        ]
        omni = [
            ('OmniROM-9', f'{out_path}\\OmniROM\\base\\android-9\\{tail_path}'),
            ('OmniROM-10', f'{out_path}\\OmniROM\\base\\android-10\\{tail_path}'),
            ('OmniROM-11', f'{out_path}\\OmniROM\\base\\android-11\\{tail_path}'),
            ('OmniROM-12', f'{out_path}\\OmniROM\\base\\android-12.0\\{tail_path}'),
            ('OmniROM-13', f'{out_path}\\OmniROM\\base\\android-13.0\\{tail_path}')
        ]
        calyx = [
            ('CalyxOS-11', f'{out_path}\\CalyxOS\\base\\android11\\{tail_path}'),
            ('CalyxOS-12', f'{out_path}\\CalyxOS\\base\\android12\\{tail_path}'),
            ('CalyxOS-13', f'{out_path}\\CalyxOS\\base\\android13\\{tail_path}')
        ]
        aospa = [
            ('aospa-quartz', f'{out_path}\\aospa\\base\\quartz-dev\\{tail_path}'),
            ('aospa-ruby', f'{out_path}\\aospa\\base\\ruby-staging\\{tail_path}'),
            ('aospa-sapphire', f'{out_path}\\aospa\\base\\sapphire\\{tail_path}'),
            ('aospa-topaz', f'{out_path}\\aospa\\base\\topaz\\{tail_path}')
        ]
        # honor = [
        #     ('honor_r', 'D:\\Honor\\match_res\\Honor\\base\\honor_r'),
        #     ('honor_s', 'D:\\Honor\\match_res\\Honor\\base\\honor_s'),
        #     ('honor_t1', 'D:\\Honor\\match_res\\Honor\\base\\honor_t`'),
        #     ('honor_t2', 'D:\\Honor\\match_res\\Honor\\base\\honor_t2'),
        #     ('honor_t3', 'D:\\Honor\\match_res\\Honor\\base\\honor_t3'),
        #     ('honor_u', 'D:\\Honor\\match_res\\Honor\\base\\honor_u'),
        # ]
        return lineage + calyx + omni + aospa


    # ins_a = IntrusiveCompare()
    # ins_a.get_intrusive_commit(lineage + calyx + omni + aospa)

    # ins_a = IntrusiveCompare()
    # ins_a.start_analysis(2, 1, lineage_s=lineage[2:], omnirom_s=omni[2:], calyx=calyx, aospa=aospa, honor=honor)
    # lineage=lineage, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor

    """
     :param
     筛选切面依赖
    """
    # res = []
    # for proj in aospa + calyx + lineage + omni + honor:
    #     f_f = FacadeFilter(proj[1], 'facade.json',
    #                        [constant.implement, constant.inherit, constant.call, constant.override, constant.R_cast,
    #                         constant.R_annotate, constant.reflect]).get_facade_conf(proj[0])
    #     res.append(f_f)
    # FileCSV.write_dict_to_csv('D:\\Honor\\match_res\\analysis\\intrusive_conf\\', 'res', res, 'w')
    # 切面top file
    # FT = FileTop('facade_file_filter.csv', ['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'],
    #              "D:\\Honor\\match_res\\facade_analysis")
    # FT.start_analysis(['e2n_e', 'e2n_n', 'n2e_n', 'n2e_e'], 1, lineage_s=lineage, omnirom_s=omni, calyx=calyx,
    #                   aospa=aospa, honor=honor)

    # file_set = ['services/core/java/com/android/server/pm/PackageManagerService.java', 'core/java/android/provider/Settings.java']
    # IntrusiveFilter('final_ownership.csv').get_inter_api(lineage, file_set)

    # honor_int = [
    #     ('D:\\Honor\\match_res\\Honor\\base\\honor_r', 'D:\\Honor\\dep_res\\android\\base\\android-11.0.0_r38.json'),
    #     ('D:\\Honor\\match_res\\Honor\\base\\honor_s', 'D:\\Honor\\dep_res\\android\\base\\android-12.1.0_r4.json'),
    # ]
    #
    # IntrusiveType().run_filter(honor_int)

    # latex表格数据格式847330820
    # ToLatex('E:\\2022ASE\\data.csv').to_latex(False)

    # 移动文件
    # method_file = ['']
    #
    result_data = ['E:\\数据\\mc\\',
                   ['file-mc_ext.csv', 'file-mc_rank_ext.csv']]
    old_paths = get_out_path('D:\\Honor\\match_res')
    new_paths = get_out_path('D:\\Honor\\match_res_new', "")
    graduate_paths = get_out_path('E:\\Graduate\\datas\\match_res_new', "")

    # for new in new_paths:
    #     FileMove.file_move(new[1], f"{result_data[0]}\\{new[0]}", result_data[1])
    patterns = ["FinalDel", "AccessibilityModify", "HiddenApi", "ParameterListModifyDep", "InheritExtension",
                "ImplementExtension", "ReflectUse"]


    # 整理开源耦合面数据
    FileMove.file_csv_aggr([new for new in graduate_paths], "facade_analysis/facade_base_info_count.csv",
                           f"E:\\Graduate\\datas\\耦合面\\毕设数据", "facade_size")
    FileMove.file_csv_aggr([new for new in graduate_paths], "facade_analysis/facade_relation_info_count.csv",
                           f"E:\\Graduate\\datas\\耦合面\\毕设数据", "facade")
    FileMove.file_csv_aggr([new for new in graduate_paths], "intrusive_analysis/final_ownership_count.csv",
                           f"E:\\Graduate\\datas\\耦合面\\毕设数据", "ownership")
    FileMove.file_csv_aggr([new for new in graduate_paths], "intrusive_analysis/intrusive_count.csv",
                           f"E:\\Graduate\\datas\\耦合面\\毕设数据", "change_type")
    # 整理闭源耦合面数据
    honor = [
        ('R', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/RRes'),
        ('S', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/SRes'),
        ('T1', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/T0Res_0710'),
        ('T2', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/ARes'),
        ('T3', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/T1Res_0710'),
        ('U', 'E:/Graduate/datas/耦合面/毕设数据/MagicOSRes/URes')
    ]
    # FileMove.file_csv_aggr([new for new in honor], "facade_base_info_count.csv",
    #                        f"E:\\Graduate\\datas\\耦合面\\毕设数据", "facade_size_h.csv")
    # FileMove.file_csv_aggr([new for new in honor], "facade_relation_info_count.csv",
    #                        f"E:\\Graduate\\datas\\耦合面\\毕设数据", "facade_h.csv")
    # FileMove.file_csv_aggr([new for new in honor], "intrusive_count.csv",
    #                        f"E:\\Graduate\\datas\\耦合面\\毕设数据", "change_type_h.csv")
    pattern_ident = ["coupling-patterns", "anti-patterns", "gra-anti-patterns"]
    for new in graduate_paths:
        MetricFilter(
            f"{new[1]}\\{pattern_ident[2]}\\res_metric_statistic.json",
            f"E:\\Graduate\\datas\\反模式\\毕设数据\\反模式分级\\{pattern_ident[2]}"
        ).handle_count(patterns, new[0])
    FileMove.file_csv_aggr(
        [new for new in graduate_paths], f"{pattern_ident[2]}/pattern_count.csv",
        f"E:\\Graduate\\datas\\反模式\\毕设数据\\反模式数量\\{pattern_ident[2]}", "pattern_count"
    )
    FileMove.file_csv_aggr([new for new in graduate_paths], f"{pattern_ident[0]}/timecost.csv",
                           f"E:\\Graduate\\datas\\反模式\\毕设数据\\性能", "内部类运行时间")
    for new in graduate_paths:
        FileMove.file_move(f"{new[1]}", f"E:\\Graduate\\datas\\反模式\\毕设数据\\性能\\{new[0]}",
                           ["vf.txt"])

    # 切面依赖模块统计
    # FacadeFilter(aospa[2][1], 'facade.json',
    #              [constant.implement, constant.inherit, constant.R_aggregate]).get_module_stat_2(f'{aospa[2][0]}_facade_stat_class')
    #
    # FacadeFilter(aospa[2][1], 'facade.json',
    #              [constant.call]).get_module_stat_2(f'{aospa[2][0]}_facade_stat_method')
    #
    # FacadeFilter(lineage[2][1], 'facade.json',
    #              [constant.implement, constant.inherit, constant.R_aggregate]).get_module_stat_2(f'{lineage[2][0]}_facade_stat_class')
    #
    # FacadeFilter(lineage[2][1], 'facade.json',
    #              [constant.call]).get_module_stat_2(f'{lineage[2][0]}_facade_stat_method')

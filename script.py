from script.script import Script
from script.intrusive import IntrusiveCompare
from script.facade_filter import FacadeFilter
from script.data_to_latex import ToLatex
from script.intrusive_type import IntrusiveType
from script.facade_top_file import FileTop
from script.intrusive_filter import IntrusiveFilter
from utils import Constant, FileCSV

import sys
import time

if __name__ == '__main__':
    Script('D:\\Honor\\source_code\\utils\\bin').run_command()
    lineage = [('lineage-16.0', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-16.0'),
               ('lineage-17.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-17.1'),
               ('lineage-18.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1'),
               ('lineage-19.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-19.1')]
    calyx = [('calyx-12', 'D:\\Honor\\match_res\\CalyxOS\\base\\android12'),
             ('calyx-11', 'D:\\Honor\\match_res\\CalyxOS\\base\\android11')]
    omni = [('omni-12', 'D:\\Honor\\match_res\\OmniROM\\base\\android-12.0'),
            ('omni-11', 'D:\\Honor\\match_res\\OmniROM\\base\\android-11'),
            ('omni-10', 'D:\\Honor\\match_res\\OmniROM\\base\\android-10'),
            ('omni-9', 'D:\\Honor\\match_res\\OmniROM\\base\\android-9')]
    aospa = [
        ('quartz', 'D:\\Honor\\match_res\\aospa\\base\\quartz-dev'),
        ('ruby', 'D:\\Honor\\match_res\\aospa\\base\\ruby-staging'),
        ('sapphire', 'D:\\Honor\\match_res\\aospa\\base\\sapphire')
    ]
    honor = [
        ('honor_r', 'D:\\Honor\\match_res\\Honor\\base\\honor_r'),
        ('honor_s', 'D:\\Honor\\match_res\\Honor\\base\\honor_s'),
    ]
    # ins_a = IntrusiveCompare()
    # ins_a.start_analysis(2, 1, lineage_s=lineage[2:], omnirom_s=omni[2:], calyx=calyx, aospa=aospa, honor=honor)
    # lineage=lineage, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor

    # 筛选切面依赖
    # res = []
    # for proj in aospa + calyx + lineage + omni + honor:
    #     f_f = FacadeFilter(proj[1], 'facade.json',
    #                        [Constant.implement, Constant.inherit, Constant.call, Constant.override, Constant.R_cast,
    #                         Constant.R_annotate, Constant.reflect]).get_facade_conf(proj[0])
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

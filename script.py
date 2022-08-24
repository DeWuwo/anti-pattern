from script.script import Script
from script.intrusive import IntrusiveCompare
from script.facade_filter import FacadeFilter
from script.data_to_latex import ToLatex
from utils import Constant

import sys
import time

if __name__ == '__main__':
    Script('D:\\Honor\\source_code\\utils\\bin').run_honor_command()
    # ins_a = IntrusiveCompare()
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
    # ins_a.start_analysis(2, 1, lineage_s=lineage[2:], omnirom_s=omni[2:], calyx=calyx, aospa=aospa, honor=honor)
    # lineage=lineage, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor

    # 筛选切面依赖
    # for proj in lineage + calyx + omni + aospa:
    #     f_f = FacadeFilter(proj[1],
    #                        [Constant.implement, Constant.inherit, Constant.call, Constant.override, Constant.R_cast,
    #                         Constant.R_annotate, Constant.reflect]).filter_hidden()

    # latex表格数据格式
    # ToLatex('E:\\2022ASE\\data.csv').to_latex()

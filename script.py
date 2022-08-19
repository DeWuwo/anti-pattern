from script.script import Script
from script.intrusive import IntrusiveCompare

import sys
import time

if __name__ == '__main__':
    # Script('D:\\Honor\\source_code\\utils\\bin').run_command()
    ins_a = IntrusiveCompare()
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
    # lineage=lineage, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor
    ins_a.start_analysis(2, 1, lineage=lineage, omnirom=omni, calyx=calyx,aospa=aospa, honor=honor)

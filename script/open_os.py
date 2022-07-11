import os

from typing import List


class OpenOS:
    LineageOS: List
    CalyxOS: List
    GraphneOs: List
    OmniROM: List
    LA: List
    AOSPA: List

    def __init__(self):
        self.LineageOS = [
            ['LineageOS', 'lineage-17.1', 'base', 'lineage-17.1', '3e199be0fcc31325bab3aea9ecd7808006b14e9d'],
            ['LineageOS', 'lineage-18.1', 'base', 'lineage-18.1', '82f6df1c2d329a128953088b662df8ed6fc6ae5b'],
            ['LineageOS', 'lineage-19.1', 'base', 'lineage-17.1', '9cdf73f7cbed891c433d278d533f0e0113d68efc'],
        ]

        self.GraphneOs = [
            ['GraphneOs', '12.1', 'base', '12.1', '5870093533eb178488e36c465e84466864420947']
        ]

        self.CalyxOS = [
            ['CalyxOS', 'android10', 'base', 'android10', '2cdeacfe733cc625462b93ddb312ecf3934b89b9'],
            ['CalyxOS', 'android11', 'base', 'android11', '8551ec363dcd7c2d7c82c45e89db4922156766ab'],
            ['CalyxOS', 'android12', 'base', 'android12', '187a94cca708cf7aa87ef875e16fed561e72679d']
        ]

        self.OmniROM = [
            ['OmniROM', 'android-10', 'base', 'android-10', '2cdeacfe733cc625462b93ddb312ecf3934b89b9'],
            ['OmniROM', 'android-11', 'base', 'android-11', 'ba595d5debf2a214e05a8a774be658b09b354d1a'],
            ['OmniROM', 'android-12.0', 'base', 'android-12.0', '4bd4cf2ac7dd470de97c673f086133b7e7e4d5d3']
        ]

        self.LA = [
            ['LA', 'LA.QSSI.12.0.r1-05800.01-qssi.0', 'base', 'LA.QSSI.12.0.r1-05800.01-qssi.0',
             '6c2cb6876a30dee0b94d946ca529e06cd96b9642']
        ]

        self.AOSPA = [
            ['aospa', 'sapphire', 'base', 'sapphire', '898ad0236f79d81514806e4f4ca3a2fe401e0705']
        ]

    # self.LA + self.LineageOS + self.GraphneOs + self.CalyxOS + self.OmniROM
    def get_all_os(self):
        return self.AOSPA


def get_path(os_name: str, os_version: str, pkg: str, os_commit, aosp_commit: str):
    aosp_code_path = os.path.join('D:\\Honor\\source_code\\android', pkg)
    assi_code_path = os.path.join('D:\\Honor\\source_code\\', os_name, pkg)
    aosp_dep_path = os.path.join('D:\\Honor\\dep_res\\android', pkg, os_version + '.json')
    assi_dep_path = os.path.join('D:\\Honor\\dep_res\\', os_name, pkg, os_version + '.json')
    out_path = os.path.join('D:\\Honor\\match_res\\', os_name, pkg, os_version)
    return aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, aosp_commit, os_commit, out_path

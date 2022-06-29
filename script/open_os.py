import os

from typing import List


class OpenOS:
    LineageOS: List
    CalyxOS: List
    GraphneOs: List
    OmniROM: List
    LA: List

    def __init__(self):
        self.LineageOS = [

            ['LineageOS', 'lineage-17.1', 'base', '3e199be0fcc31325bab3aea9ecd7808006b14e9d'],
            ['LineageOS', 'lineage-18.1', 'base', '82f6df1c2d329a128953088b662df8ed6fc6ae5b'],
            ['LineageOS', 'lineage-19.1', 'base', '9cdf73f7cbed891c433d278d533f0e0113d68efc'],

        ]

        self.GraphneOs = [
            ['GraphneOs', '12.1', 'base', '5870093533eb178488e36c465e84466864420947']
        ]

        self.CalyxOS = [
            ['CalyxOS', 'android10', 'base', '2cdeacfe733cc625462b93ddb312ecf3934b89b9'],
            ['CalyxOS', 'android11', 'base', '8551ec363dcd7c2d7c82c45e89db4922156766ab'],
            ['CalyxOS', 'android12', 'base', '187a94cca708cf7aa87ef875e16fed561e72679d']
        ]

        self.OmniROM = [
            ['OmniROM', 'android-10', 'base', '2cdeacfe733cc625462b93ddb312ecf3934b89b9'],
            ['OmniROM', 'android-11', 'base', 'ba595d5debf2a214e05a8a774be658b09b354d1a'],
            ['OmniROM', 'android-12.0', 'base', '4bd4cf2ac7dd470de97c673f086133b7e7e4d5d3']
        ]

        self.LA = [
            ['LA', 'LA.QSSI.12.0.r1-05800.01-qssi.0', 'base', '6c2cb6876a30dee0b94d946ca529e06cd96b9642']
        ]

    def get_all_os(self):
        return self.LineageOS + self.GraphneOs + self.CalyxOS + self.OmniROM


def get_path(os_name: str, os_commit: str, pkg: str, aosp_commit: str):
    aosp_code_path = os.path.join('D:\\Honor\\source_code\\android', pkg)
    assi_code_path = os.path.join('D:\\Honor\\source_code\\', os_name, pkg)
    aosp_dep_path = os.path.join('D:\\Honor\\dep_res\\android', pkg, aosp_commit + '.json')
    assi_dep_path = os.path.join('D:\\Honor\\dep_res\\', os_name, pkg, os_commit + '.json')
    out_path = os.path.join('D:\\Honor\\match_res\\', os_name, pkg, os_commit)
    return aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, aosp_commit, os_commit, out_path

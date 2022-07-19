import os

from typing import List


class OpenOS:
    LineageOS: List
    CalyxOS: List
    GraphneOs: List
    OmniROM: List
    LA: List
    AOSPA: List
    test: List

    def __init__(self):
        self.LineageOS = [
            ['LineageOS', 'lineage-16.0', 'base', 'd56f59389212df5462b342be7600c1974d27c0d5',
             'ad31dbbdcd76091d7d2d1fc6c863ee17c3bfe87d'],
            ['LineageOS', 'lineage-17.1', 'base', '44f7cdc0ef98074572a572b6aa78d1c0a23420f7',
             'dff3deab5d25f8bbfd49abfb423043c9be47b7db'],
            ['LineageOS', 'lineage-18.1', 'base', '7f7fc2562a95be630dbe609e8fb70383dcfada4f',
             '49d8b986dddd441df741698541788c5f3a9c465f'],
            ['LineageOS', 'lineage-19.1', 'base', '484c59b972c1772f75a4b1b9fce7512eee517dcb',
             '9cdf73f7cbed891c433d278d533f0e0113d68efc'],
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

        self.test = [
            ['LineageOS', 'lineage-16.0', 'base', 'd56f59389212df5462b342be7600c1974d27c0d5',
             'ad31dbbdcd76091d7d2d1fc6c863ee17c3bfe87d'],
            ['LineageOS', 'lineage-17.1', 'base', '44f7cdc0ef98074572a572b6aa78d1c0a23420f7',
             'dff3deab5d25f8bbfd49abfb423043c9be47b7db'],
            ['LineageOS', 'lineage-18.1', 'base', '7f7fc2562a95be630dbe609e8fb70383dcfada4f',
             '49d8b986dddd441df741698541788c5f3a9c465f'],
            ['LineageOS', 'lineage-19.1', 'base', '484c59b972c1772f75a4b1b9fce7512eee517dcb',
             '9cdf73f7cbed891c433d278d533f0e0113d68efc'],
        ]

    # self.LA + self.LineageOS + self.GraphneOs + self.CalyxOS + self.OmniROM
    def get_all_os(self):
        return self.test
        # return self.LineageOS + self.GraphneOs + self.CalyxOS + self.OmniROM + self.AOSPA + self.LA


def get_path(os_name: str, os_version: str, pkg: str, os_commit, aosp_commit: str):
    aosp_code_path = os.path.join('D:\\Honor\\source_code\\android', pkg)
    assi_code_path = os.path.join('D:\\Honor\\source_code\\', os_name, pkg)
    aosp_dep_path = os.path.join('D:\\Honor\\dep_res\\android', pkg, aosp_commit + '.json')
    assi_dep_path = os.path.join('D:\\Honor\\dep_res\\', os_name, pkg, os_commit + '.json')
    out_path = os.path.join('D:\\Honor\\match_res\\', os_name, pkg, os_version)
    return aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, aosp_commit, os_commit, out_path

import os

from typing import List


class OpenOS:
    LineageOS: List
    CalyxOS: List
    OmniROM: List
    AOSPA: List
    test: List
    source_code_path: str
    source_dep_path: str
    out_path: str
    android: dict

    def __init__(self):
        self.source_code_path = 'D:\\Honor\\source_code\\'
        self.source_dep_path = 'D:\\Honor\\dep_res\\'
        # self.out_path = 'D:\\Honor\\match_res_new\\'
        # 毕设输出路径
        self.out_path = 'E:\\Graduate\\datas\\match_res_new'
        self.android = {
            'android-12': 'cebf5c06997b64f4e47a1611edb5f97044509d76',
            'android-11': '34a1b9c951c38537ab96b69bc308f6e0884823f5',
            'android-10': '57bb140be9e48cf08acba131f7463e461777bb8e',
            'android-9': '6549309f6c473b792ec62d1aebadec62bcf07827'
        }
        """
        伴生系统名称 伴生系统版本， 伴生系统仓，伴生系统节点，原生系统节点，伴生hidden，原生hidden，原生版本(useless)
        """
        self.LineageOS = [
            ['LineageOS', 'lineage-16.0', 'base', 'd56f59389212df5462b342be7600c1974d27c0d5',
             'ad31dbbdcd76091d7d2d1fc6c863ee17c3bfe87d', 'null', 'null', 'android-9'],
            ['LineageOS', 'lineage-17.1', 'base', 'f5600fff5c1fe764b568c7c885eb1aee022a81ca',
             '2cdeacfe733', 'null', 'null', 'android-10'],
            ['LineageOS', 'lineage-18.1', 'base', '7f7fc2562a95be630dbe609e8fb70383dcfada4f',
             '49d8b986dddd441df741698541788c5f3a9c465f', 'hiddenapi-flags-lineage18.csv', 'hiddenapi-flags-11.csv',
             'android-11'],
            ['LineageOS', 'lineage-19.1', 'base', '484c59b972c1772f75a4b1b9fce7512eee517dcb',
             '9cdf73f7cbed891c433d278d533f0e0113d68efc', 'hiddenapi-flags-lineage19.csv', 'hiddenapi-flags-12.csv',
             'android-12'],
            ['LineageOS', 'lineage-20.0', 'base', 'e33699a6fd9e692b2332b3c10642d49af617234e',
             'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['LineageOS', 'lineage-20.0', 'base', '3af7ee5c7fd07853b9579f64cc48fb398e6b4b9b',
            #  '5c8d1d9774e465bb40d45096b2bc5eba77b261d6', 'null', 'null', 'android-12'],
            # ['LineageOS', 'lineage-21.0', 'base', 'bd2fc2feee2009b186dbb83487ee804574caa3c4',
            #  'c43d4f80b2913fec5303d59136041d336c6537e7', 'null', 'null', 'android-12'],

        ]

        self.CalyxOS = [
            ['CalyxOS', 'android11', 'base', '687846d3b443e9a740c73d628c60f3d725f4a95c', '49d8b986dddd', 'null',
             'null', 'android-11'],
            ['CalyxOS', 'android12', 'base', 'ca93c649fb376e572dc9fcc1242fd9ba316c37d7', '187a94cca708', 'null', 'null',
             'android-12'],
            ['CalyxOS', 'android13', 'base', '1ab0b23a1d46b60a76015f090ada435f10bc9ecd',
             'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['CalyxOS', 'android13', 'base', 'd42f8d774901e8bcdf2c83b61b01fad79ce2f69f',
            # '5c8d1d9774e465bb40d45096b2bc5eba77b261d6', 'null', 'null', 'android-12']
        ]

        self.OmniROM = [
            ['OmniROM', 'android-9', 'base', 'fb069e3b9c5744327bf62231dfc08e03d7e4502f', '988624eda2c5', 'null',
             'null', 'android-9'],
            ['OmniROM', 'android-10', 'base', '8c60ca7c0b3fbe4fca6d3ec3137d76127cfe7c77',
             '2cdeacfe733cc625462b93ddb312ecf3934b89b9', 'null', 'null', 'android-10'],
            ['OmniROM', 'android-11', 'base', 'a362a5abfe0dbcf48877c5b02d1a8da8d9c504c6',
             'ba595d5debf2a214e05a8a774be658b09b354d1a', 'null', 'null', 'android-11'],
            ['OmniROM', 'android-12.0', 'base', 'c4f3170b13b0189af9b8addebf3587bd013576c6',
             '4bd4cf2ac7dd470de97c673f086133b7e7e4d5d3', 'null', 'null', 'android-12'],
            ['OmniROM', 'android-13.0', 'base', '20b50bcf2cdd722955040b713056399f0ec17bd2',
             'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['OmniROM', 'android-13.0', 'base', '47f9587ecc53e367420cf4406f7564180a89838f',
            #  '2391f0824ac30b5fba264f01fc6e4ae75db9c2f4', 'null', 'null', 'android-12'],
            # ['OmniROM', 'android-14.0', 'base', '573d4753f10107c5bccec853c57889b283bf1485',
            #  'c43d4f80b2913fec5303d59136041d336c6537e7', 'null', 'null', 'android-12'],

        ]

        self.AOSPA = [
            ['aospa', 'quartz-dev', 'base', '42d2107a29219428453ac8de3e4f46f270af763c', '823838e9efc3', 'null', 'null',
             'android-10'],
            ['aospa', 'ruby-staging', 'base', '3b08012599a6b4fb556dddd1e1e8972b2a2730fe', 'ca05b4c5f776', 'null',
             'null', 'android-11'],
            ['aospa', 'sapphire', 'base', '15d9159eb00fb7fd92f9dc249af588f655fd8f66',
             '898ad0236f79d81514806e4f4ca3a2fe401e0705', 'null', 'null', 'android-12'],
            ['aospa', 'topaz', 'base', '74a21b9',
             'd69be73', 'null', 'null', 'android-12'],
            # ['aospa', 'topaz', 'base', 'da4e6b0612a340b211f987fecb5db178aff14400',
            #  '5d817b262e54712b60ff317837ae7f78c7fabfdc', 'null', 'null', 'android-12'],
        ]

        self.test = [
            ['LineageOS', 'lineage-16.0', 'base', 'd56f59389212df5462b342be7600c1974d27c0d5',
             'ad31dbbdcd76091d7d2d1fc6c863ee17c3bfe87d', 'null', 'null', 'android-9'],
            # ['LineageOS', 'lineage-18.1', 'base', '7f7fc2562a95be630dbe609e8fb70383dcfada4f',
            #  '49d8b986dddd441df741698541788c5f3a9c465f', 'hiddenapi-flags-lineage18.csv', 'hiddenapi-flags-11.csv',
            #  'android-11'],
            # ['OmniROM', 'android-11', 'base', 'a362a5abfe0dbcf48877c5b02d1a8da8d9c504c6',
            #  'ba595d5debf2a214e05a8a774be658b09b354d1a', 'null', 'null', 'android-11'],
            # ['aospa', 'sapphire', 'base', '15d9159eb00fb7fd92f9dc249af588f655fd8f66', '898ad0236f79d81514806e4f4ca3a2fe401e0705', 'null', 'null', 'android-12'],
            # ['LineageOS', 'lineage-20.0', 'base', 'e33699a6fd9e692b2332b3c10642d49af617234e',
            #  'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['LineageOS', 'lineage-21.0_conf', 'base', 'bd2fc2feee2009b186dbb83487ee804574caa3c4',
            #  'c43d4f80b2913fec5303d59136041d336c6537e7', 'null', 'null', 'android-12'],
            # ['CalyxOS', 'android13', 'base', '1ab0b23a1d46b60a76015f090ada435f10bc9ecd',
            #  'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['OmniROM', 'android-13.0', 'base', '20b50bcf2cdd722955040b713056399f0ec17bd2',
            #  'af0429f7c3314ac83bc537bf6281dc78f55bcccf', 'null', 'null', 'android-12'],
            # ['OmniROM', 'android-14.0_conf', 'base', '573d4753f10107c5bccec853c57889b283bf1485',
            #  'c43d4f80b2913fec5303d59136041d336c6537e7', 'null', 'null', 'android-12'],
            # ['aospa', 'topaz', 'base', '74a21b9',
            #  'd69be73', 'null', 'null', 'android-12'],
        ]

    # -nc D:\Honor\source_code\android\base 49d8b986dddd441df741698541788c5f3a9c465f D:\Honor\source_code\LineageOS\base 7f7fc2562a95be630dbe609e8fb70383dcfada4f -json E:\test\1.json
    # -c D:\Honor\source_code\LineageOS\base 3874e9c876bac28279c389a8e6cb82ad951546dc -json E:\test\2.json
    def get_all_os(self):
        # return self.test
        return self.LineageOS + self.CalyxOS + self.OmniROM + self.AOSPA

    def get_path(self, os_name: str, os_version: str, pkg: str, os_commit, aosp_commit: str, os_hidden: str,
                 aosp_hidden, aosp_base_version: str):
        aosp_code_path = os.path.join(self.source_code_path, 'android', pkg)
        assi_code_path = os.path.join(self.source_code_path, os_name, pkg)
        aosp_dep_path = os.path.join(self.source_dep_path, 'android', pkg, aosp_commit + '.json')
        assi_dep_path = os.path.join(self.source_dep_path, os_name, pkg, os_commit + '.json')
        base_aosp_dep_path = os.path.join(self.source_dep_path, os_name, pkg, self.android[aosp_base_version] + '.json')
        out_path = os.path.join(self.out_path, os_name, pkg, os_version)
        if os_hidden != 'null':
            aosp_hidden_path = os.path.join(self.source_dep_path, 'android', aosp_hidden)
            aosp_hidden = f' -hd {aosp_hidden_path}'
            os_hidden_path = os.path.join(self.source_dep_path, os_name, os_hidden)
            os_hidden = f' -hd {os_hidden_path}'
        else:
            aosp_hidden = ''
            os_hidden = ''
        return aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, base_aosp_dep_path, aosp_commit, os_commit, \
               self.android[aosp_base_version], out_path, aosp_hidden, os_hidden

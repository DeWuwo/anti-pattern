import json
import os
from typing import List, Dict


class FileReader:
    outFile = ['/diff.json', '/section.json', '/example.json', '/anti-patterns.json', '/stat.json']
    outTitle = ['diff', 'section', 'example', 'anti-patterns', 'stat']

    @classmethod
    def read_from_json(cls, fileAndroid, fileHonor: str):
        print('reading file...')
        try:
            with open(fileHonor, encoding='utf-8') as h:
                honor = json.load(h, strict=False)
                entities_honor = honor['variables']
                cells_honor = honor['cells']
                entities_stat_honor = honor["entityNum"]
            with open(fileAndroid) as a:
                android = json.load(a, strict=False)
                entities_aosp = android['variables']
                cells_aosp = android['cells']
                entities_stat_aosp = android["entityNum"]
            print('file read success')
            return entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp
        except Exception as e:
            raise e

    @classmethod
    def write_to_json(cls, outPath: str, section: list, mode):
        os.makedirs(outPath, exist_ok=True)
        with open(outPath + cls.outFile[mode], 'w+', encoding='utf-8') as o:
            json.dump({cls.outTitle[mode]: section}, o, ensure_ascii=False, indent=4)

    @classmethod
    def write_match_mode(cls, outPath: str, matchSet: List[Dict]):
        for item in matchSet:
            for mode in item:
                mode_path = outPath + '/' + mode
                os.makedirs(mode_path, exist_ok=True)
                for index, exa in enumerate(item[mode]):
                    exa_path = mode_path + '/' + str(index)
                    os.makedirs(exa_path, exist_ok=True)
                    cls.write_to_json(exa_path, exa, 2)

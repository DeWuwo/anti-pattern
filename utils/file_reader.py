import json
import os
import csv
from typing import List, Dict


class FileReader:
    outFile = ['/diff.json', '/section.json', '/example.json', '/anti-patterns.json', '/stat.json']
    outTitle = ['diff', 'section', 'example', 'anti-patterns', 'stat']

    @classmethod
    def read_from_json(cls, file_android, file_honor: str):
        print('reading file...')
        try:
            with open(file_honor, encoding='utf-8') as h:
                honor = json.load(h, strict=False)
                entities_honor = honor['variables']
                cells_honor = honor['cells']
                entities_stat_honor = honor["entityNum"]
            with open(file_android) as a:
                android = json.load(a, strict=False)
                entities_aosp = android['variables']
                cells_aosp = android['cells']
                entities_stat_aosp = android["entityNum"]
            print('file read success')
            return entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp
        except Exception as e:
            raise e

    @classmethod
    def read_from_csv(cls, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                entities = []
                reader = csv.reader(f)
                next(reader)
                for entity in reader:
                    if entity[4] != '[]':
                        entities.append(int(entity[2]))
                return entities
            except Exception as e:
                raise e

    @classmethod
    def write_to_json(cls, out_path: str, section, mode):
        os.makedirs(out_path, exist_ok=True)
        with open(out_path + cls.outFile[mode], 'w+', encoding='utf-8') as o:
            json.dump({cls.outTitle[mode]: section}, o, ensure_ascii=False, indent=4)

    @classmethod
    def write_match_mode(cls, out_path: str, match_set: List[Dict]):
        for item in match_set:
            for mode in item:
                mode_path = out_path + '/' + mode
                os.makedirs(mode_path, exist_ok=True)
                for index, exa in enumerate(item[mode]):
                    exa_path = mode_path + '/' + str(index)
                    os.makedirs(exa_path, exist_ok=True)
                    cls.write_to_json(exa_path, exa, 2)

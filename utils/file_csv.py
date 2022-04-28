import csv
import os
from datetime import date
from typing import Dict


class FileCSV:
    @classmethod
    def read_from_file_csv(cls, file_path: str) -> list:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                info = [line for line in reader]
                return info
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
    def write_stat_to_csv(cls, out_path: str, run_time: date, assi: str, aosp: str, res: dict):
        file_exist = False
        file_path = os.path.join(out_path, 'res.csv')
        if os.path.exists(file_path):
            file_exist = True
        # get header
        headers = ['run_time', 'assi', 'aosp']
        for key in res:
            headers.append(key)
        # get res
        res.update({'run_time': run_time, 'assi': assi, 'aosp': aosp})
        os.makedirs(out_path, exist_ok=True)
        with open(os.path.join(out_path, 'res.csv'), 'a', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            if not file_exist:
                f_writer.writeheader()
            f_writer.writerow(res)

    @classmethod
    def write_to_csv(cls, out_path: str, name: str, headers: list, statistic: Dict[str, dict]):
        file_path = os.path.join(out_path, name + '.csv')
        with open(file_path, 'w', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            f_writer.writeheader()
            for key in statistic:
                f_writer.writerow(statistic[key])

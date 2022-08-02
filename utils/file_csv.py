import os
import csv
import pandas as pd
from datetime import date
from typing import Dict, List, Any
from model.entity import Entity


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
    def write_stat_to_csv(cls, out_path: str, name: str, run_time: date, assi: str, assi_pkg: str, assi_version: str,
                          res: dict):
        file_exist = False
        file_path = os.path.join(out_path, name + '_res.csv')
        if os.path.exists(file_path):
            file_exist = True
        # get header
        headers = ['run_time', 'assi', 'assi_pkg', 'assi_version']
        for key in res:
            headers.append(key)
        # get res
        res.update({headers[0]: run_time, headers[1]: assi, headers[2]: assi_pkg, headers[3]: assi_version})
        os.makedirs(out_path, exist_ok=True)
        with open(file_path, 'a', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            if not file_exist:
                f_writer.writeheader()
            f_writer.writerow(res)

    @classmethod
    def write_to_csv(cls, out_path: str, name: str, headers: list, statistic: Dict[Any, dict]):
        file_path = os.path.join(out_path, name + '.csv')
        with open(file_path, 'w', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            f_writer.writeheader()
            for key in statistic:
                f_writer.writerow(statistic[key])

    @classmethod
    def merge_csv(cls, left: str, right: str, columns: List[str], output: str, name: str):
        fl = pd.read_csv(left)
        fr = pd.read_csv(right)
        all_data = pd.merge(fl, fr, how='left', on=columns)
        all_data.to_csv(os.path.join(output, 'file-mc-' + name + '.csv'))

    @classmethod
    def dump_ent_commit_infos(cls, ent_commit_infos, file_name: str):
        with open(file_name, "w", newline="") as file:
            writer = csv.DictWriter(file, ["Entity", "category", "id", "param_names", "file path", "commits",
                                           "base commits", "accompany commits"])
            writer.writeheader()
            for row in ent_commit_infos:
                writer.writerow(row)

    @classmethod
    def write_dict_to_csv(cls, out_path: str, name: str, data: List[dict]):
        file_path = os.path.join(out_path, name + '.csv')
        headers = []
        if data:
            headers = [item for item in data[0].keys()]
        with open(file_path, 'w', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            f_writer.writeheader()
            f_writer.writerows(data)

    @classmethod
    def write_owner_to_csv(cls, out_path: str, name: str, data: List[Entity]):
        file_path = os.path.join(out_path, name + '.csv')
        headers = []
        if data:
            headers = [item for item in data[0].to_owner().keys()]
        with open(file_path, 'w', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            f_writer.writeheader()
            for item in data:
                f_writer.writerow(item.to_owner())

    @classmethod
    def write_entity_to_csv(cls, out_path: str, name: str, data: List[Entity], to_format: str):
        file_path = os.path.join(out_path, name + '.csv')
        headers = []
        if data:
            headers = [item for item in data[0].handle_to_format(to_format).keys()]
        with open(file_path, 'w', newline='') as f:
            f_writer = csv.DictWriter(f, headers)
            f_writer.writeheader()
            for item in data:
                f_writer.writerow(item.handle_to_format(to_format))

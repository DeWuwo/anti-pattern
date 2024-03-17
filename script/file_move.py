import os

from utils import Command, FileCSV
from typing import List


class FileMove:
    @classmethod
    def file_move(cls, src_path: str, dest_path: str, file_set: List[str]):
        for file in file_set:
            src_file = os.path.join(src_path, file)
            dest_file = os.path.join(dest_path)
            if not os.path.exists(dest_file):
                os.makedirs(dest_file)
            print(src_file, dest_file)
            Command.command_run(f'copy /Y {src_file} {dest_file}')

    @classmethod
    def file_csv_aggr(cls, src_paths: List[tuple], file: str, dest_path: str, out_name: str):
        res = []
        for src_path in src_paths:
            src_file = os.path.join(src_path[1], file)
            dest_file = os.path.join(dest_path)
            if not os.path.exists(dest_file):
                os.makedirs(dest_file)
            data = {"project": src_path[0]}
            data.update(FileCSV.read_dict_from_csv(src_file)[0])
            res.append(data)
        FileCSV.write_dict_to_csv(dest_path, f"{out_name}", res, "a", False)

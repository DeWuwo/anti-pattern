import os
from utils import FileCSV


class EntityOwner:
    @classmethod
    def get_diff_files(cls, file_path: str):
        diff_file_list = []
        for file in FileCSV.read_from_csv(file_path)[1:]:
            diff_file_list.append(file.replace("/", '_').replace("\\", '_'))
        return diff_file_list


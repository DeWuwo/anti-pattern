from typing import Dict
from utils.file_csv import FileCSV


class BlameField:
    file_path: str
    module_blame: Dict

    def __init__(self, file_path):
        self.file_path = file_path
        self.module_blame = {}

    def read_blame_field(self):
        reader_res = FileCSV.read_from_file_csv(self.file_path)
        for blame in reader_res:
            self.module_blame[blame[1] + blame[2]] = blame[3]

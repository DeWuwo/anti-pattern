import os
from typing import List

from utils import FileCSV


class ToLatex:
    file_path: str
    relation_types: List[str]

    def __init__(self, file_path: str):
        self.file_path = file_path

    def to_latex(self):
        load_data: List[list] = FileCSV.read_from_file_csv(self.file_path, True)
        for line in load_data:
            index = 0
            for data in line:
                index += 1
                format_str = data
                if '%' in data:
                    format_str = data.split('%')[0] + '\\%'
                if index == len(line):
                    format_str += '\\\\\n'
                else:
                    format_str += ' &'
                print(format_str, end='')

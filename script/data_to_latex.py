import os
from typing import List

from utils import FileCSV


class ToLatex:
    file_path: str
    relation_types: List[str]

    def __init__(self, file_path: str):
        self.file_path = file_path

    def to_latex(self):
        load_data: List[list] = FileCSV.read_from_file_csv(self.file_path)
        for line in load_data:
            for data in line:
                format_str = data
                if '%' in data:
                    format_str = data.split('%')[0] + '\\%'
                if line.index(data) == len(line) - 1:
                    format_str += '\\\\\n'
                else:
                    format_str += ' &'
                print(format_str, end='')

import os
from typing import List

from utils import FileCSV


class ToLatex:
    file_path: str
    relation_types: List[str]

    """
    该脚本用于读取表格数据并将其转化未 latex 所需文本，方便论文数据更新
    具体内容格式可再调整
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def to_latex(self, flag):
        load_data: List[list] = FileCSV.read_from_file_csv(self.file_path, True)
        gray_color = ''
        if flag:
            gray_color = '\\cellcolor{gray}'
        for line in load_data:
            index = 0
            for data in line:
                index += 1
                format_str = data
                if '%' in data:
                    format_str = data.split('%')[0] + '\\%'
                if data.isalnum():
                    if int(data) == 0:
                        format_str = gray_color + format_str
                    else:
                        format_str = '{:,}'.format(int(format_str))
                if index == len(line):
                    format_str += '\\\\\n'
                else:
                    format_str += ' &'
                print(format_str, end='')

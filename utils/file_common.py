import os
import re
from typing import List
from utils import FileCSV


class FileCommon:
    @classmethod
    def read_from_file_by_line(cls, file_path: str) -> List[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                res = []
                for line in f.readlines():
                    line = line.strip('\n')
                    if "\"" in line:
                        print(line)
                        res.append(re.findall(r"\"(.+?)\"", line)[0])
                return res
        except Exception as e:
            raise e

    @classmethod
    def get_files_list(cls, dir_path: str, base_type: List[str]):
        target = dir_path
        file_list = []
        for parent, dirs, files in os.walk(target):
            for f in files:
                if f.split('.')[-1] in base_type:
                    file_list.append(os.path.join(parent, f).split(dir_path, 1)[1].strip('\\').strip('/'))
        return file_list


if __name__ == '__main__':
   for file in FileCommon.get_files_list('D:\\Honor\\source_code\\android\\base\\services\\core\\java\\com\\android\\server\\pm', ['java']):
       print(file)

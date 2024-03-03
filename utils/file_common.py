import os
import re
import linecache
from typing import List
from utils import FileCSV
from time import time


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
    def read_file_to_line(cls, file_path, start_line, end_line):
        res = []
        for line_number in range(start_line, end_line + 1):
            res.append(linecache.getline(file_path, line_number))
        return res

    @classmethod
    def read_file_to_line_compact(cls, file_path, start_line, end_line):
        res = []
        for line_number in range(start_line, end_line + 1):
            res.append(cls.compact_string(linecache.getline(file_path, line_number)))
        return res

    @classmethod
    def read_file_to_scope(cls, file_path, start_line, start_col, end_line, end_col):
        end_col = end_col + 1
        if start_line == end_line:
            return [linecache.getline(file_path, start_line)[start_col: end_col]]
        res = [linecache.getline(file_path, start_line)[start_col:]]
        for line_number in range(start_line + 1, end_line):
            line = linecache.getline(file_path, line_number)
            res.append(line)
        res.append(linecache.getline(file_path, end_line)[:end_col])
        return res

    @classmethod
    def read_file_to_scope_compact(cls, file_path, start_line, start_col, end_line, end_col):
        end_col = end_col + 1
        if start_line == end_line:
            return [cls.compact_string(linecache.getline(file_path, start_line)[start_col: end_col])]
        res = [cls.compact_string(linecache.getline(file_path, start_line)[start_col:])]
        for line_number in range(start_line + 1, end_line):
            line = cls.compact_string(linecache.getline(file_path, line_number))
            res.append(line)
        res.append(cls.compact_string(linecache.getline(file_path, end_line)[:end_col]))
        return res

    @classmethod
    def get_files_list(cls, dir_path: str, base_type: List[str]):
        target = dir_path
        file_list = []
        for parent, dirs, files in os.walk(target):
            for f in files:
                if f.split('.')[-1] in base_type:
                    file_list.append(os.path.join(parent, f).split(dir_path, 1)[1].strip('\\').strip('/'))
        return file_list

    @classmethod
    def compact_string(cls, string: str):
        return ''.join(string.split())


if __name__ == '__main__':
    start_time = time()
    print(FileCommon.read_file_to_scope(
        'D:\\Honor\\source_code\\aospa\\base\\packages/SystemUI/src/com/android/systemui/statusbar/phone/StatusBar.java',
        264, 32, 264, 54))
    end_time = time()
    print('git blame cost', end_time - start_time)

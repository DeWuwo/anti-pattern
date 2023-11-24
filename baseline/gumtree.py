import os
from utils import FileJson


class Gumtree:
    @classmethod
    def get_diff_files(cls, file_path: str):
        file_list = []
        for parent, dirs, files in os.walk(file_path):
            for f in files:
                file_list.append(os.path.join(parent, f).strip('\\').strip('/'))

        diff_file_list = []
        for file in file_list:
            res = FileJson.read_base_json(file)
            try:
                if res['actions']:
                    diff_file_list.append(file.rsplit("\\", 1)[1].replace(".json", ".java"))
            except KeyError:
                continue
            except Exception as e:
                continue
        return diff_file_list

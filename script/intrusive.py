import os
from typing import List
from utils import FileCSV


class IntrusiveCompare:
    dimension: List[str]
    file_name: str
    out_path: str

    def __init__(self):
        self.file_name = 'final_ownership_file_count.csv'
        self.dimension = ['native', 'absolutely native', 'intrusive', 'extensive']
        self.out_path = "D:\\Honor\\match_res\\intrusive_analysis"

    def get_top_files(self, projects: List[tuple[str, str]], dim: int, top: float):

        def fetch_top(file_list: List[dict], scope: int) -> List[dict]:
            temp = []
            for index in range(scope):
                if file_list[index][self.dimension[dim]] == '':
                    break
                temp.append(file_list[index])
            return temp

        p_top_files: List[set] = []
        p_top_files_data = []
        for project in projects:
            v_ins = FileCSV.read_dict_from_csv(os.path.join(project[1], self.file_name))
            sorted_files = sorted(v_ins, key=lambda x: get_num(x[self.dimension[dim]]), reverse=True)
            top_files = fetch_top(sorted_files, int(len(sorted_files) * top))
            p_top_files_data.append(top_files)
            p_top_files.append(set([file['file'] for file in top_files]))
        return p_top_files, p_top_files_data

    def write_res(self, projects: List[tuple[str, str]], top_files: List[set], top_files_data: List[List[dict]],
                  top: float):
        for data, project in zip(top_files_data, projects):
            FileCSV.write_dict_to_csv(self.out_path, project[0] + '-' + str(top), data)

        union_file = top_files[0]
        for p_top in top_files:
            union_file = union_file & p_top

        FileCSV.base_write_to_csv(self.out_path, 'union_top_files', list(union_file))

    def start_analysis(self, projects: List[tuple[str, str]], dim: int, top: float):
        p_top_files, p_top_files_data = self.get_top_files(projects, dim, top)
        self.write_res(projects, p_top_files, p_top_files_data, top)


def get_num(str_num: str):
    if str_num == '' or str_num == 'null':
        return 0
    else:
        return int(str_num)


if __name__ == '__main__':
    ins_a = IntrusiveCompare()
    projects = [('lineage-16.0', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-16.0'),
                ('lineage-17.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-17.1'),
                ('lineage-18.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1'),
                ('lineage-19.1', 'D:\\Honor\\match_res\\LineageOS\\base\\lineage-19.1')]
    ins_a.start_analysis(projects, 2, 0.1)

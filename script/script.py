import os
from time import time
from typing import List
from script.open_os import OpenOS
from utils import Command, FileCommon, FileCSV, FileJson
from baseline.compare import Compare


class Script:
    ref_path: str
    proj_path: str
    gum_path: str
    oss: OpenOS
    dep_path: str
    out_path: str

    def __init__(self, ref_path):
        self.ref_path = ref_path
        self.proj_path = 'D:\\Honor\\realization\\section\\base-enre-out\\'
        self.oss = OpenOS()
        self.dep_path = 'D:\\Honor\\source_code\\enre_java_honor_0715.jar'
        self.gum_path = 'D:\\Honor\\source_code\\gumtree.jar'
        self.gum_out = "D:\\Honor\\gumdiff"

    def get_command(self, aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, base_aosp_dep_path, aosp_commit,
                    assi_commit, aosp_base_commit, out_path, aosp_hidden, assi_hidden):
        self.out_path = out_path

        def compare():
            # 比较ref结果
            old: dict = FileJson.read_base_json(os.path.join(out_path, 'unsure_resolution.json'))
            new: dict = FileJson.read_base_json(os.path.join(out_path, 'refactor_entities.json'))
            old_ents = old.keys()
            new_ents = new.keys()
            cmp_res = {}
            cmp_res["old_count"] = len(old_ents)
            cmp_res["new_count"] = len(new_ents)
            cmp_res["same"] = len(list(set(old_ents) & set(new_ents)))
            cmp_res["left"] = [int(num) for num in list(set(old_ents) - set(new_ents))]
            cmp_res["right"] = [int(num) for num in (list(set(new_ents) - set(old_ents)))]
            cmp_res["left"].sort()
            cmp_res["right"].sort()
            FileCSV.write_dict_to_csv("E:\\Graduate\\baseline\\test", "refcmp", [cmp_res], 'a', False)

        # compare()

        branch_checkout_commands: List[str] = [
            # f'git -C {aosp_code_path} clean -d -fx',
            # f'git -C {aosp_code_path} checkout .',
            # f'git -C {aosp_code_path} checkout {aosp_base_commit}',

            f'git -C {aosp_code_path} clean -d -fx',
            f'git -C {aosp_code_path} checkout .',
            f'git -C {aosp_code_path} checkout {aosp_commit}',

            f'git -C {assi_code_path} clean -d -fx',
            f'git -C {assi_code_path} checkout .',
            f'git -C {assi_code_path} checkout {assi_commit}',
        ]

        dep_commands: List[str] = [
            # f'java -Xmx20g -jar {self.dep_path} java {aosp_code_path} base -o {aosp_base_commit}{aosp_hidden}',
            # f'move /Y {self.proj_path}{aosp_base_commit}.json {base_aosp_dep_path}',
            f'java -Xmx20g -jar {self.dep_path} java {aosp_code_path} base -o {aosp_commit}{aosp_hidden}',
            f'move /Y {self.proj_path}{aosp_commit}.json {aosp_dep_path}',
            f'java -Xmx20g -jar {self.dep_path} java {assi_code_path} base -o {assi_commit}{assi_hidden}',
            f'move /Y {self.proj_path}{assi_commit}.json {assi_dep_path}',
        ]

        if not os.path.exists(os.path.join(out_path, 'mc')):
            os.makedirs(os.path.join(out_path, 'mc'))

        if os.path.exists(aosp_dep_path) and os.path.exists(assi_dep_path):
            dep_commands = []

        # ref_util = os.path.join(self.ref_path, 'RefactoringMiner')
        # ref_out = os.path.join(out_path, 'refactor.json')
        # ref_commands: List[str] = [
        #     f'{ref_util} -nc {aosp_code_path} {aosp_commit} {assi_code_path} {assi_commit} -json {ref_out}'
        # ]

        detect_commands: List[str] = [
            f'python main.py -rpa {aosp_code_path} -rpe {assi_code_path} -rela {aosp_dep_path} -rele {assi_dep_path} ' +
            f'-ca {aosp_commit} -ce {assi_commit} -ref {self.ref_path} -o {out_path}'
        ]
        return branch_checkout_commands, dep_commands, detect_commands

    def run_gum_diff(self, aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, base_aosp_dep_path,
                     aosp_commit,
                     assi_commit, aosp_base_commit, out_path, aosp_hidden, assi_hidden):
        gum_commands: List[str] = []
        pkg = r"services\core\java\com\android\server\pm"
        os.makedirs(os.path.join(out_path, 'gumdiff'), exist_ok=True)
        for file in FileCommon.get_files_list(os.path.join(aosp_code_path, pkg), ['java']):
            up_path = os.path.join(aosp_code_path, pkg, file).replace('/', '\\')
            down_path = os.path.join(assi_code_path, pkg, file).replace('/', '\\')
            out = os.path.join(out_path, 'gumdiff',
                               os.path.join(pkg, file.replace('.java', '.json')).replace("\\", '_').replace(
                                   "/", '_'))
            gum_commands.append(
                f"java -jar {self.gum_path} textdiff -f json {up_path} {down_path} > {out}", )
        return gum_commands

    def run_command(self):
        for item in self.oss.get_all_os():
            branch_checkout_commands, dep_commands, detect_commands = self.get_command(
                *self.oss.get_path(*item))
            for cmd in branch_checkout_commands:
                print(cmd)
                Command.command_run(cmd)
            for cmd in dep_commands:
                print(cmd)
                Command.command_run(cmd)
            for cmd in detect_commands:
                print(cmd)
                Command.command_run(cmd)

            # gumdiff
            # gum_diff_cmd = self.run_gum_diff(*self.oss.get_path(*item))
            # start_time = time()
            # for cmd in gum_diff_cmd:
            #     Command.command_run(cmd)
            # end_time = time()
            # FileCSV.write_dict_to_csv('E:\\Graduate\\baseline\\gumdiff', 'runtime',
            #                           [{'count': len(gum_diff_cmd), 'time': end_time - start_time}], 'a')
            # Compare().compare_file_gumtree(self.out_path)

            # 生成ref
            # start_time = time()
            # for cmd in ref_commands:
            #     Command.command_run(cmd)
            # end_time = time()
            # FileCSV.write_dict_to_csv('E:\\Graduate\\baseline\\RefactoringMiner', 'runtime',
            #                           [{'time': end_time - start_time}], 'a')

    def get_honor_command(self):
        commands: List[str] = []
        aosp_code_path = 'D:\\HONOR_code\\RAOSP\\base'
        assi_code_path = 'D:\\HONOR_code\\RMagicUI\\base'
        aosp_dep_path = 'D:\\merge\\res\\RAOSP\\base\\base-out-RAOSP.json'
        assi_dep_path = 'D:\\merge\\res\\RMagicUI\\base\\base-out-Rmagic.json'
        out_path = 'D:\\merge\\res\\RmagicUI\\base'
        if not os.path.exists(os.path.join(out_path, 'mc')):
            os.makedirs(os.path.join(out_path, 'mc'))
        # commands.append(f'git -C {assi_code_path} log --numstat --date=iso > {out_path}/mc/gitlog')
        commands.append(
            f'python main.py -ra {aosp_code_path} -re {assi_code_path} -a {aosp_dep_path} -e {assi_dep_path} -ref {self.ref_path} -o {out_path}')
        aosp_code_path = 'D:\\HONOR_code_final\\SAOSP_r2\\base'
        assi_code_path = 'D:\\HONOR_code_final\\SMagicUI\\base'
        aosp_dep_path = 'D:\\HONOR_code_final\\S_result_final\\base\\base-out_SAOSP_r2.json'
        assi_dep_path = 'D:\\HONOR_code_final\\S_result_final\\base\\base-out_SmagicUI.json'
        out_path = 'D:\\HONOR_code_final\\S_result_final\\base\\'
        if not os.path.exists(os.path.join(out_path, 'mc')):
            os.makedirs(os.path.join(out_path, 'mc'))
        # commands.append(f'git -C {assi_code_path} log --numstat --date=iso > {out_path}/mc/gitlog')
        commands.append(
            f'python main.py -ra {aosp_code_path} -re {assi_code_path} -a {aosp_dep_path} -e {assi_dep_path} -ref {self.ref_path} -o {out_path}')
        # T
        aosp_code_path = 'D:\\HONOR_code_final\\TAOSP_r1\\base'
        assi_code_path = 'D:\\HONOR_code_final\\TMagicUI\\base'
        aosp_dep_path = 'D:\\HONOR_code_final\\T_result_final\\base\\base-out_TAOSP_r1.json'
        assi_dep_path = 'D:\\HONOR_code_final\\T_result_final\\base\\base-out_TmagicUI.json'
        out_path = 'D:\\HONOR_code_final\\T_result_final\\base\\'
        if not os.path.exists(os.path.join(out_path, 'mc')):
            os.makedirs(os.path.join(out_path, 'mc'))
        commands.append(
            f'python main.py -ra {aosp_code_path} -re {assi_code_path} -a {aosp_dep_path} -e {assi_dep_path} -ref {self.ref_path} -o {out_path}')

        return commands

    def run_honor_command(self):
        commands = self.get_honor_command()
        for cmd in commands:
            Command.command_run(cmd)

    def get_dep(self):
        aosp_code_path = 'D:\\Honor\\source_code\\android\\base'
        base_aosp_dep_path = 'D:\\Honor\\dep_res\\android\\base\\test'
        aosp_base_commit = 'android-12.0.0_r1'
        dep_path = 'D:\\Honor\\source_code\\enre_java_1.2.1.jar'
        cmds = [
            f'git -C {aosp_code_path} clean -d -fx',
            f'git -C {aosp_code_path} checkout .',
            f'git -C {aosp_code_path} checkout {aosp_base_commit}',
            f'java -Xmx20g -jar {dep_path} java {aosp_code_path} base -o {aosp_base_commit}',
            f'move /Y {self.proj_path}{aosp_base_commit}.json {base_aosp_dep_path}',
        ]
        for cmd in cmds:
            Command.command_run(cmd)

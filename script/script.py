import os

from typing import List
from script.open_os import OpenOS
from utils import Command


class Script:
    ref_path: str
    proj_path: str
    oss: OpenOS
    dep_path: str

    def __init__(self, ref_path):
        self.ref_path = ref_path
        self.proj_path = 'D:\\Honor\\realization\\section\\base-enre-out\\'
        self.oss = OpenOS()
        self.dep_path = 'D:\\Honor\\source_code\\enre_java_1.1.6.jar'

    def get_command(self, aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, aosp_commit, assi_commit,
                    out_path, aosp_hidden, assi_hidden):
        branch_checkout_commands: List[str] = [
            f'git -C {aosp_code_path} clean -d -fx',
            f'git -C {aosp_code_path} checkout .',
            f'git -C {aosp_code_path} checkout {aosp_commit}',

            f'git -C {assi_code_path} clean -d -fx',
            f'git -C {assi_code_path} checkout .',
            f'git -C {assi_code_path} checkout {assi_commit}',
        ]
        dep_commands: List[str] = [
            f'java -Xmx20g -jar {self.dep_path} java {aosp_code_path} base -o {aosp_commit}{aosp_hidden}',
            f'move /Y {self.proj_path}{aosp_commit}.json {aosp_dep_path}',
            f'java -Xmx20g -jar {self.dep_path} java {assi_code_path} base -o {assi_commit}{assi_hidden}',
            f'move /Y {self.proj_path}{assi_commit}.json {assi_dep_path}',
        ]

        if os.path.exists(aosp_dep_path) and os.path.exists(assi_dep_path):
            dep_commands = []

        detect_commands: List[str] = [
            f'python main.py -ca {aosp_code_path} -cc {assi_code_path} -a {aosp_dep_path} -c {assi_dep_path} -ref {self.ref_path} -o {out_path}'
        ]
        return branch_checkout_commands, dep_commands, detect_commands

    def run_command(self):
        for item in self.oss.get_all_os():
            branch_checkout_commands, dep_commands, detect_commands = self.get_command(*self.oss.get_path(*item))
            for cmd in branch_checkout_commands:
                print(cmd)
                Command.command_run(cmd)
            for cmd in dep_commands:
                print(cmd)
                Command.command_run(cmd)
            for cmd in detect_commands:
                print(cmd)
                Command.command_run(cmd)

    def get_honor_command(self):
        commands: List[str] = []
        aosp_code_path = 'D:\\HONOR_code\\RAOSP\\base'
        assi_code_path = 'D:\\HONOR_code\\RMagicUI\\base'
        aosp_dep_path = 'D:\\merge\\res\\RAOSP\\base\\base-out-RAOSP.json'
        assi_dep_path = 'D:\\merge\\res\\RMagicUI\\base\\base-out-Rmagic.json'
        out_path = 'D:\\merge\\res\\RmagicUI\\base'
        commands.append(
            f'python main.py -ca {aosp_code_path} -cc {assi_code_path} -a {aosp_dep_path} -c {assi_dep_path} -ref {self.ref_path} -o {out_path}')
        aosp_code_path = 'D:\\HONOR_code_final\\SAOSP_r2\\base'
        assi_code_path = 'D:\\HONOR_code_final\\SMagicUI\\base'
        aosp_dep_path = 'D:\\HONOR_code_final\\S_result_final\\base\\base-out_SAOSP_r2.json'
        assi_dep_path = 'D:\\HONOR_code_final\\S_result_final\\base\\base-out_SmagicUI.json'
        out_path = 'D:\\HONOR_code_final\\S_result_final\\base\\'
        commands.append(
            f'python main.py -ca {aosp_code_path} -cc {assi_code_path} -a {aosp_dep_path} -c {assi_dep_path} -ref {self.ref_path} -o {out_path}')

        return commands

    def run_honor_command(self):
        commands = self.get_honor_command()
        for cmd in commands:
            Command.command_run(cmd)

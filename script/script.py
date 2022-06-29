from typing import List
from script.open_os import OpenOS, get_path
from utils import Command


class Script:
    ref_path: str
    proj_path: str
    oss: OpenOS

    def __init__(self, ref_path):
        self.ref_path = ref_path
        self.proj_path = 'D:\\Honor\\realization\\section'
        self.oss = OpenOS()

    def get_command(self, aosp_code_path, assi_code_path, aosp_dep_path, assi_dep_path, aosp_commit, assi_commit,
                    out_path):
        commands: List[str] = [
            # f'cd {aosp_code_path}',
            f'git -C {aosp_code_path} clean -d -fx',
            f'git -C {aosp_code_path} checkout .',
            f'git -C {aosp_code_path} checkout {aosp_commit}',
            # f'cd {assi_code_path}',
            f'git -C {assi_code_path} clean -d -fx',
            f'git -C {assi_code_path} checkout .',
            f'git -C {assi_code_path} checkout {assi_commit}',
            # f'cd {self.proj_path}',
            f'python main.py -ca {aosp_code_path} -cc {assi_code_path} -a {aosp_dep_path} -c {assi_dep_path} -ref {self.ref_path} -o {out_path}'
        ]
        return commands

    def run_command(self):
        for item in self.oss.get_all_os():
            commands = self.get_command(*get_path(*item))
            for cmd in commands:
                Command.command_run(cmd)


from utils import Command, FileCSV


class CodeTracker:
    root_path: str

    def __init__(self):
        self.root_path = "E:\\Graduate\\codeTracker\\code-tracker\\target\\code-tracker-2.6-SNAPSHOT.jar"

    def run(self, repo_path: str, up_commit: str, down_commit: str, dep_path: str, files: str, out_path: str):
        command_line = f"java -jar {self.root_path} -r {repo_path} -uc {up_commit} -dc {down_commit} -dp {dep_path} -f {files} -o {out_path}"
        print(command_line)
        Command.command_run(command_line)

    def load_res(self, file_path):
        res = FileCSV.read_dict_from_csv(file_path)

    def res_to_base(self, change_type: list):
        to_base_dict = {
            'Body Change': 'body_modify',
            'Add Parameter': 'param_modify',
            'Remove Parameter': 'param_modify',
            'Rename Parameter': 'param_modify',
            "Extract Method": 'extracted',
            "Rename": 'rename',

        }
        pass

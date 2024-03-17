from utils import Command, FileCSV


class CodeTracker:
    root_path: str
    change_type: dict

    def __init__(self):
        self.root_path = "E:\\Graduate\\codeTracker\\code-tracker\\target\\code-tracker-2.6-SNAPSHOT.jar"
        self.change_type = {
            "access modifier change": "access_modify",
            "modifier change": "modifier_modify",
            "body change": "body_modify",
            "rename": "rename",
            "documentation change": "body_modify",
            "type change": "type_modify",
            "container change": "",
            "annotation change": "annotation_modify",
            "parameter change": "param_modify",
            "return type change": "return_type_modify",
            "Extract Method": 'extracted',
            "moved": 'move',
            "introduced": 'introduced'
        }

    def run(self, repo_path: str, up_commit: str, down_commit: str, dep_path: str, files: str, out_path: str):
        command_line = f"java -jar {self.root_path} -r {repo_path} -uc {up_commit} -dc {down_commit} -dp {dep_path} -f {files} -o {out_path}"
        print(command_line)
        Command.command_run(command_line)

    def load_res(self, file_path):
        res = []
        entities = FileCSV.read_dict_from_csv(file_path)
        for ent in entities:
            ent_id = int(ent["id"])
            ownership = "actively native"
            modify = [self.change_type[change] for change in ent["changeType"].split("+") if change != '']
            if modify:
                if "introduced" in modify or "extracted" in modify:
                    ownership = "extensive"
                else:
                    ownership = "intrusive native"
            modify = set([change for change in modify if change != "introduced"])
            res.append([ent_id, ownership, modify])
        return res

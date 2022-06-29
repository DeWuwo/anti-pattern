import subprocess
from subprocess import CalledProcessError


class Command:
    @classmethod
    def command_run(cls, command: str):
        try:
            ret = subprocess.run(command, shell=True, check=True, encoding="utf-8")
            return ret.returncode == 0
        except CalledProcessError:
            print(f'command run error --- {command}')

import csv
import sys
import os
from pathlib import Path
from typing import Set, IO

import git

from model.blamer.dep_blamer import get_sha


def get_all_commits(repo: git.Repo) -> Set[git.Commit]:
    return set(repo.iter_commits('HEAD'))


def write_all_commits(fp: IO, commits: Set[git.Commit]):
    writer = csv.DictWriter(fp, ["commit"])
    writer.writeheader()
    for commit in commits:
        writer.writerow({"commit": str(commit)})


def entry():
    repo_path_base = sys.argv[1]
    repo_path_accompany = sys.argv[2]
    tag = get_sha(Path(repo_path_accompany))
    repo_base = git.Repo(repo_path_base)
    repo_accompany = git.Repo(repo_path_accompany)
    base_commits = get_all_commits(repo_base)
    accompany_commits = get_all_commits(repo_accompany)
    only_accompany_commits = accompany_commits.difference(base_commits)

    with open(f"{Path(repo_path_base).name}_base_commits.csv", "w", newline="") as file:
        write_all_commits(file, base_commits)

    with open(f"{Path(repo_path_accompany).name}_{tag}_accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, accompany_commits)

    with open(f"{Path(repo_path_accompany).name}_{tag}_only_accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, only_accompany_commits)


def entry_get_commits(repo_path_base, repo_path_accompany, out_path):
    tag = get_sha(Path(repo_path_accompany))
    repo_base = git.Repo(repo_path_base)
    repo_accompany = git.Repo(repo_path_accompany)
    base_commits = get_all_commits(repo_base)
    accompany_commits = get_all_commits(repo_accompany)
    only_accompany_commits = accompany_commits.difference(base_commits)
    os.makedirs(out_path, exist_ok=True)
    with open(f"{out_path}/base_commits.csv", "w", newline="") as file:
        write_all_commits(file, base_commits)

    with open(f"{out_path}/accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, accompany_commits)

    with open(f"{out_path}/only_accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, only_accompany_commits)


if __name__ == '__main__':
    entry()

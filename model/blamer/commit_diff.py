import csv
import sys
import os
from pathlib import Path
from typing import Set, IO

import git

from model.blamer.dep_blamer import get_sha
from utils import Command


def get_all_commits(repo: git.Repo) -> Set[str]:
    return set([str(commit) for commit in repo.iter_commits('HEAD')])


def get_all_aosp_commits(repo: git.Repo) -> Set[str]:
    all_commits = set()
    # for tag in repo.remote().refs:
    for tag in repo.tags:
        all_commits = all_commits | set([str(commit) for commit in repo.iter_commits(tag)])
    return all_commits


def get_all_aosp_commits_by_command(repo: git.Repo) -> Set[str]:
    # all_commits = git.Git(repo.working_dir).execute(["git", "rev-list", "--all"])
    # git rev-list --all
    commits = repo.iter_commits("--all")
    commit_hashes = [commit.hexsha for commit in commits]
    return set(commit_hashes)


def read_all_commits(file_path: str) -> Set[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            commits = []
            reader = csv.reader(f)
            next(reader)
            for commit in reader:
                commits.append(commit[0])
        except Exception as e:
            raise e
    return set(commits)


def write_all_commits(fp: IO, commits: Set[str]):
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


# 基于diff 获取差异文件
def get_diff_files(repo_path_accompany, aosp_commit, extensive_commit):
    aosp_modify_list = []
    extensive_modify_list = []
    for file_changed in git.Repo(repo_path_accompany).commit(aosp_commit).diff(extensive_commit):
        aosp_modify_list.append(file_changed.a_path)
        extensive_modify_list.append(file_changed.b_path)


def entry_get_commits(repo_path_base, repo_path_accompany, out_path):
    tag = get_sha(Path(repo_path_accompany))
    repo_base = git.Repo(repo_path_base)
    repo_accompany = git.Repo(repo_path_accompany)
    if os.path.exists(f"{out_path}/all_base_commits.csv"):
        all_base_commits = read_all_commits(f"{out_path}/all_base_commits.csv")
    else:
        all_base_commits = get_all_aosp_commits_by_command(repo_base)
        with open(f"{out_path}/all_base_commits.csv", "w", newline="") as file:
            write_all_commits(file, all_base_commits)
    base_commits = get_all_commits(repo_base)
    accompany_commits = get_all_commits(repo_accompany)
    possible_accompany_commits = accompany_commits.difference(base_commits)
    old_base_commits = possible_accompany_commits.intersection(all_base_commits)
    only_accompany_commits = possible_accompany_commits - old_base_commits

    os.makedirs(out_path, exist_ok=True)

    with open(f"{out_path}/base_commits.csv", "w", newline="") as file:
        write_all_commits(file, base_commits)

    with open(f"{out_path}/accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, accompany_commits)

    with open(f"{out_path}/possible_accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, possible_accompany_commits)

    with open(f"{out_path}/old_base_commits.csv", "w", newline="") as file:
        write_all_commits(file, old_base_commits)

    with open(f"{out_path}/only_accompany_commits.csv", "w", newline="") as file:
        write_all_commits(file, only_accompany_commits)


if __name__ == '__main__':
    print(get_diff_files("D:\\Honor\\source_code\\LineageOS\\base", "9cdf73f7cbed891c433d278d533f0e0113d68efc",
                         "484c59b972c1772f75a4b1b9fce7512eee517dcb"))

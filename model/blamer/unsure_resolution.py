import csv
import sys
import json
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Dict
import argparse
import git

from model.blamer.move_detect import distill_move_edit_list, MoveEdit

refactor_move_cache: Dict[str, List[MoveEdit]] = {}


def search_refactoring(category: str, longname: str, unsure_params: str, unsure_filepath: str,
                       refactor_data: List[dict], commit: str) -> List[MoveEdit]:
    try:
        move_edits = refactor_move_cache[commit]
    except KeyError:
        move_edits = distill_move_edit_list(refactor_data)
        refactor_move_cache[commit] = move_edits
    ret = []
    for move in move_edits:
        to_state = move.to_state
        if category == to_state.get_category() and to_state.longname() == longname and \
                Path(move.to_state.file_path) == Path(unsure_filepath) and \
                (unsure_params == "null" or to_state.get_param() == unsure_params):
            ret.append(move)

    return ret


def search_refactoring_by_id(refactor_data: List[dict]) -> List[MoveEdit]:
    move_edits = distill_move_edit_list(refactor_data)
    ret = []
    for move in move_edits:
        ret.append(move)

    return ret


OwnerShipData = Dict[str, str]


def resolve_unsure(repo_path: Path, not_sure_line: OwnerShipData, refactor_data: Dict[str, List[dict]], flag: bool) \
        -> Optional[List[MoveEdit]]:
    if flag:
        unsure_id = not_sure_line['id']
        related_moves = search_refactoring_by_id(refactor_data[unsure_id])
    else:
        repo = git.Repo(repo_path)
        third_party_commits = json.loads(not_sure_line["accompany commits"])
        sorted_commits = list(sorted(third_party_commits,
                                     key=lambda k: repo.commit(k).committed_datetime, reverse=False))
        commit = repo.commit(sorted_commits[0])
        unsure_longname = not_sure_line["Entity"]
        unsure_filepath = not_sure_line["file path"]
        unsure_param = not_sure_line["param_names"]
        unsure_category = not_sure_line["category"]
        if unsure_category == 'Variable':
            return None
        related_moves = search_refactoring(unsure_category, unsure_longname, unsure_param, unsure_filepath,
                                           refactor_data[str(commit)], str(commit))
    return related_moves if related_moves else None


RefactorData = Dict[str, List[dict]]


def load_refactor_data(file_path: Path, ref_data) -> RefactorData:
    ret = defaultdict(list)
    if ref_data:
        for r in ref_data:
            ret[r["sha1"]] = r["refactorings"]
        return ret
    refactor_obj = json.loads(file_path.read_text())
    for r in refactor_obj["commits"]:
        ret[r["sha1"]] = r["refactorings"]
    return ret


def load_refactor_data_id(file_path: Path) -> RefactorData:
    refactor_obj: dict = json.loads(file_path.read_text())
    ret = defaultdict(list)
    for k, v in refactor_obj.items():
        ret[k] = v['Moves']
    return ret


def load_not_sure_lines(file_path: Path) -> List[OwnerShipData]:
    head = ["Entity", "category", "id", "param_names", "file path", "commits", "base commits", "third party commits"]
    ret = []
    with open(file_path) as file:
        reader = csv.DictReader(file, head)
        reader.__next__()
        for row in reader:
            ret.append(dict(row))

    return ret


def resolution_entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refactor_path", dest="refactor_path", action="store")
    parser.add_argument("--repo", dest="repo_path", action="store")
    parser.add_argument("--unsure_ownership", dest="unsure_ownership", action="store")
    parser.add_argument("-o", dest="output", action="store")
    args = parser.parse_args()

    refactor_path = Path(args.refactor_path)
    repo_path = Path(args.repo_path)
    unsure_ownership = args.unsure_ownership

    refactor_data = load_refactor_data(refactor_path)
    not_sure_rows = load_not_sure_lines(Path(unsure_ownership))

    move_list = list()

    for row in not_sure_rows:
        moves = resolve_unsure(repo_path, row, refactor_data)
        if moves:
            row_dict = dict()
            for k, v in row.items():
                try:
                    row_dict[k] = json.loads(v)
                except json.JSONDecodeError:
                    row_dict[k] = v
            row_dict["Moves"] = [m.refactor_obj for m in moves]
            move_list.append(row_dict)

    out_name = args.output if args.output else "unsure_resolution.json"
    with open(out_name, "w") as file:
        json.dump(move_list, file, indent=4)


def diff_re_divide_owner(repo_path: str, refactor_path: str, ref_data: List, unsure_refactor: str,
                         not_sure_rows: List[dict], out_path: str):
    refactor_path = Path(refactor_path)
    repo_path = Path(repo_path)
    unsure_path = Path(unsure_refactor)
    # unsure_ownership = unsure_ownership
    refactor_cache = False
    if unsure_path.exists():
        refactor_data = load_refactor_data_id(unsure_path)
        refactor_cache = True
    else:
        refactor_data = load_refactor_data(refactor_path, ref_data)
    # not_sure_rows = load_not_sure_lines(Path(unsure_ownership))

    move_list_write: Dict[int, dict] = {}
    move_list: Dict[int, list] = {}

    i = 0
    total = len(not_sure_rows)
    for row in not_sure_rows:
        i += 1
        print("\r", end="")
        print(f"       Refactor detect: {i}/{total}", end="")
        sys.stdout.flush()
        moves = resolve_unsure(repo_path, row, refactor_data, refactor_cache)
        if moves:
            row_dict = dict()
            for k, v in row.items():
                try:
                    row_dict[k] = json.loads(v)
                except json.JSONDecodeError:
                    row_dict[k] = v
            row_dict["Moves"] = [m.refactor_obj for m in moves]
            move_list_write[int(row_dict['id'])] = row_dict
            move_list[int(row_dict['id'])] = [row_dict,
                                              [[m.refactor_obj['type'], m.src_state, m.to_state] for m in moves]]
    with open(f"{out_path}/unsure_resolution.json", "w") as file:
        json.dump(move_list_write, file, indent=4)
    return move_list


if __name__ == '__main__':
    resolution_entry()

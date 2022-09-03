import os
import csv
import json
from typing import List
from pathlib import Path
from model.blamer.commit_diff import entry_get_commits
from model.blamer.dep_blamer import get_entity_commits
from model.blamer.tagging_ownership import get_entity_owner
from model.blamer.unsure_resolution import diff_re_divide_owner
from model.blamer.refactor_format import get_name_from_sig
from utils import Command, FileJson


class EntityOwner:
    repo_path_base: str
    repo_path_accompany: str
    accompany_relation_path: str
    refactor_miner: str
    out_path: str
    ref_miner_data: List

    def __init__(self, repo_path_base: str, repo_path_accompany: str, accompany_relation_path: str, refactor_miner: str,
                 out_path: str):
        self.repo_path_base = repo_path_base
        self.repo_path_accompany = repo_path_accompany
        self.accompany_relation_path = accompany_relation_path
        self.refactor_miner = refactor_miner
        self.out_path = out_path
        self.pre_run()

    def get_path(self, short_path: str):
        return os.path.join(self.out_path, short_path)

    def pre_run(self):
        os.makedirs(self.out_path, exist_ok=True)
        print('start get all commits')
        self.get_commits_and_ref()
        print('start get all entities\' commits')
        self.get_entity_commits()

    def get_commits_and_ref(self):
        extension_commits = entry_get_commits(self.repo_path_base, self.repo_path_accompany, self.out_path)
        print('run refactoring miner')
        ref_res = self.get_refactor(extension_commits)
        self.ref_miner_data = ref_res

    def get_entity_commits(self):
        try:
            get_entity_commits(self.repo_path_accompany, self.accompany_relation_path,
                               self.get_path('old_base_commits.csv'), self.get_path('only_accompany_commits.csv'),
                               self.out_path, self.out_path)
        except Exception as e:
            print('blame run error:', e)

    def divide_owner(self):
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = \
            get_entity_owner(self.get_path('base_commits.csv'), self.get_path('old_base_commits.csv'),
                             self.get_path('only_accompany_commits.csv'), self.get_path('ownership.csv'), self.out_path)

        return all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities

    def get_refactor(self, commits: List[str]):
        ref_tool = os.path.abspath(os.path.join(self.refactor_miner, 'RefactoringMiner'))
        repo_path = self.repo_path_accompany
        ref_cache = self.get_path('ref.json')
        ref_temp_cache = self.get_path('ref_temp.json')
        if os.path.exists(ref_cache):
            return []
        ref_miner_res = []
        for commit in commits:
            cmd = f'{ref_tool} -c {repo_path} {commit} -json {ref_temp_cache}'
            try:
                Command.command_run(cmd)
                refactor_obj = json.loads(Path(ref_temp_cache).read_text())
                ref_miner_res.append(refactor_obj['commits'][0])
            except:
                pass
            if os.path.exists(ref_temp_cache):
                del_temp = f'del {ref_temp_cache}'
                Command.command_run(del_temp)
        try:
            FileJson.base_write_to_json(self.out_path, 'commits', ref_miner_res, 'ref.json', 'w')
            return []
        except:
            return ref_miner_res

    def re_divide_owner(self, not_sure_rows):
        print('   get refactor info')
        try:
            return diff_re_divide_owner(self.repo_path_accompany, self.get_path('ref.json'), self.ref_miner_data,
                                        self.get_path('unsure_resolution.json'), not_sure_rows, self.out_path)
        except Exception as e:
            print(e)

    def dump_ent_commit_infos(self, ent_commit_infos):
        with open(self.get_path('unsure_entities.csv'), "w", newline="") as file:
            writer = csv.DictWriter(file, ["Entity", "category", "id", "param_names", "file path", "commits",
                                           "base commits", "old base commits", "accompany commits"])
            writer.writeheader()
            for row in ent_commit_infos:
                writer.writerow(row)


def get_rename_source(sig: str):
    return get_name_from_sig(sig)

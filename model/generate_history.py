import os
import csv
import json
import time
import git
from typing import List
from pathlib import Path
from model.blamer.commit_diff import entry_get_commits
from model.blamer.dep_blamer import get_entity_commits
from model.blamer.tagging_ownership import get_entity_owner
from model.blamer.unsure_resolution import load_entity_refactor
from model.blamer.refactor_format import get_name_from_sig
from model.blamer.refactor import Refactor
from utils import Command, FileJson, DynamicThread


class GenerateHistory:
    repo_path_aosp: str
    repo_path_accompany: str
    accompany_relation_path: str
    refactor_miner: str
    out_path: str
    ref_miner_data: List
    aosp_modify_files: List
    extensive_modify_files: List

    def __init__(self, repo_path_aosp: str, repo_path_accompany: str, aosp_commit: str, accompany_commit: str,
                 accompany_relation_path: str, refactor_miner: str,
                 out_path: str):
        self.repo_path_aosp = repo_path_aosp
        self.repo_path_accompany = repo_path_accompany
        self.aosp_commit = aosp_commit
        self.accompany_commit = accompany_commit
        self.accompany_relation_path = accompany_relation_path
        self.refactor_miner = refactor_miner
        self.out_path = out_path
        self.aosp_modify_files = []
        self.extensive_modify_files = []
        self.pre_run()

    def get_path(self, short_path: str):
        return os.path.join(self.out_path, short_path)

    def pre_run(self):
        os.makedirs(self.out_path, exist_ok=True)
        print('start get gitlog')
        self.get_git_log()
        print('start get all commits')
        self.get_commits_and_ref()
        print('start get all entities\' commits')
        self.get_entity_commits()

    def get_git_log(self):
        commands = []
        if not os.path.exists(os.path.join(self.out_path, 'mc')):
            os.makedirs(os.path.join(self.out_path, 'mc'))
        if not os.path.exists(os.path.join(self.out_path, 'mc', 'gitlog_ext')):
            commands.append(
                f'git -C {self.repo_path_accompany} log --numstat --date=iso > {self.out_path}/mc/gitlog_ext')
        if not os.path.exists(os.path.join(self.out_path, 'mc', 'gitlog_nat')):
            commands.append(f'git -C {self.repo_path_aosp} log --numstat --date=iso > {self.out_path}/mc/gitlog_nat')
        for cmd in commands:
            Command.command_run(cmd)

    def get_diff_files(self):
        for file_changed in git.Repo(self.repo_path_accompany).commit(self.aosp_commit).diff(self.accompany_commit):
            self.aosp_modify_files.append(file_changed.a_path)
            self.extensive_modify_files.append(file_changed.b_path)

    def get_commits_and_ref(self):
        entry_get_commits(self.repo_path_aosp, self.repo_path_accompany, self.out_path)
        ref_cache = self.get_path('refactor.json')
        if os.path.exists(ref_cache):
            self.ref_miner_data = []
        else:
            print('run refactoring miner')
            t1 = time.perf_counter()
            ref_res = self.get_refactor()
            t2 = time.perf_counter()
            FileJson.base_write_to_json(self.out_path, 'commits', ref_res, 'refactor.json', 'w')
            print(f'ger refactor data time cost: {t2 - t1} s')
            self.ref_miner_data = ref_res

    def get_entity_commits(self):
        self.get_diff_files()
        try:
            get_entity_commits(self.repo_path_accompany, self.accompany_relation_path,
                               self.get_path('old_base_commits.csv'), self.get_path('only_accompany_commits.csv'),
                               self.out_path, self.out_path)
        except Exception as e:
            print('blame run error:', e)

    def divide_owner(self):
        all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities = \
            get_entity_owner(self.get_path('base_commits.csv'), self.get_path('old_base_commits.csv'),
                             self.get_path('only_accompany_commits.csv'), self.get_path('entity_commits'), self.out_path)

        return all_entities, all_native_entities, old_native_entities, old_update_entities, intrusive_entities, old_intrusive_entities, pure_accompany_entities

    def get_refactor(self):
        ref_tool = os.path.abspath(os.path.join(self.refactor_miner, 'RefactoringMiner'))
        ref_temp_cache = self.get_path(f'refactor.json')
        ref_miner_res = []
        cmd = f'{ref_tool} -nc {self.repo_path_aosp} {self.aosp_commit} {self.repo_path_accompany} {self.accompany_commit} -json {ref_temp_cache}'
        try:
            Command.command_run(cmd)
            refactor_obj = json.loads(Path(ref_temp_cache).read_text())
            ref_miner_res.append(refactor_obj['commits'][0])
            # ref_miner_res[refactor_obj['commits'][0]['sha1']] = refactor_obj['commits'][0]
        except:
            pass
        if os.path.exists(ref_temp_cache):
            os.remove(ref_temp_cache)
            # del_temp = f'del {ref_temp_cache}'
            # Command.command_run(del_temp)
        return ref_miner_res

    def load_refactor_entity(self, entity_possible_refactor):
        print('   get refactor info')
        try:
            t1 = time.perf_counter()
            res = Refactor(self.out_path).fetch_refactor_entities(entity_possible_refactor,
                                                                  self.get_path('refactor.json'))

            t2 = time.perf_counter()
            print(f'\n get entity refactor data time cost: {t2 - t1} s')
            return res
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

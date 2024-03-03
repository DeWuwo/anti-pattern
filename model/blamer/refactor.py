import csv
import sys
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Dict
import argparse
import git
from model.blamer.refminer_paser import RefMinerPaser


class Refactor:
    out_path: str

    def __init__(self, out_path):
        self.out_path = out_path

    def load_refactor_entity(self, entities: Dict[int, dict], refactor_res_path: str):
        refactor_data = RefMinerPaser.get_refactoring_of_first_commit(Path(refactor_res_path))
        parse_all_refactors = RefMinerPaser.distill_move_edit_list(refactor_data)

        refactor_entities_list_write: Dict[int, dict] = {}
        refactor_entities_list: Dict[int, list] = {}

        total = len(entities)
        i = 0
        for ent in entities.values():
            i += 1
            print("\r", end="")
            print(f"       Refactor detect: {i}/{total}", end="")
            sys.stdout.flush()

            unsure_longname = ent["Entity"]
            unsure_filepath = ent["file path"]
            unsure_params = ent["param_names"]
            unsure_category = ent["category"]
            ent_refactors = []
            try:
                for refactor in parse_all_refactors[unsure_category + unsure_longname]:
                    to_state = refactor.to_state
                    if unsure_params == "null" or to_state.get_param() == unsure_params:
                        ent_refactors.append(refactor)
            except KeyError:
                continue
            row_dict = dict()
            for k, v in ent.items():
                try:
                    row_dict[k] = json.loads(v)
                except json.JSONDecodeError:
                    row_dict[k] = v
            row_dict["Moves"] = [m.refactor_obj for m in ent_refactors]
            refactor_entities_list_write[int(row_dict['id'])] = row_dict
            refactor_entities_list[int(row_dict['id'])] = [row_dict,
                                                           [[m.refactor_obj['type'], m.src_state, m.to_state] for m in
                                                            ent_refactors]]

        with open(f"{self.out_path}/refactor_entities.json", "w") as file:
            json.dump(refactor_entities_list_write, file, indent=4)
        return refactor_entities_list

    def load_refactor_entity_from_file_cache(self, entities: Dict[int, dict], refactor_entities_path: Path):
        refactor_data = self.load_refactor_data_id(refactor_entities_path)
        refactor_entities_list: Dict[int, list] = {}
        for ent_id, moves in refactor_data.items():
            parse_moves = RefMinerPaser.distill_move_edit_list(moves)
            if not parse_moves:
                # 跳转至正常重新加载
                pass
            # current_moves = list(parse_moves.values())[0]
            for current_moves in list(parse_moves.values()):
                try:
                    if current_moves[0].to_state.get_category() != entities[int(ent_id)]['category']:
                        continue
                    row_dict = dict()
                    for k, v in entities[int(ent_id)].items():
                        try:
                            row_dict[k] = json.loads(v)
                        except json.JSONDecodeError:
                            row_dict[k] = v
                    row_dict["Moves"] = [m.refactor_obj for m in current_moves]
                    refactor_entities_list[int(row_dict['id'])] = [row_dict,
                                                                   [[m.refactor_obj['type'], m.src_state, m.to_state] for m
                                                                    in current_moves]]
                except KeyError:
                    print("key error")
                    pass
        return refactor_entities_list

    def fetch_refactor_entities(self, entities: Dict[int, dict], refactor_path: str):
        refactor_entities_path = Path(self.out_path, "refactor_entities.json")
        if refactor_entities_path.exists():
            refactor_res = self.load_refactor_entity_from_file_cache(entities, refactor_entities_path)
        else:
            refactor_res = self.load_refactor_entity(entities, refactor_path)
        return refactor_res

    def load_refactor_data_id(self, file_path: Path) -> Dict[str, List[dict]]:
        refactor_obj: dict = json.loads(file_path.read_text())
        ret = defaultdict(list)
        for k, v in refactor_obj.items():
            ret[k] = v['Moves']
        return ret


if __name__ == '__main__':
    print(Path("111", "222"))

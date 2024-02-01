import json
from pathlib import Path
from typing import List, Dict
from model.blamer.move_detect import MoveEdit, MoveMethodRefactorings, MoveClassRefactoring, MoveParamRefactorings, \
    extract_state


class RefMinerPaser:
    @classmethod
    def get_refactoring_of_first_commit(cls, file_path: Path) -> List[dict]:
        ret = []
        # if ref_data:
        #     for r in ref_data:
        #         ret[r["sha1"]] = r["refactorings"]
        #     return ret
        refactor_obj = json.loads(file_path.read_text())
        for r in refactor_obj["commits"]:
            ret = r["refactorings"]
        return ret

    @classmethod
    def distill_move_edit_list(cls, refactor_objs: List[dict]) -> Dict[str, List[MoveEdit]]:
        # ret = []
        # for refactor_obj in refactor_objs:
        #     ret.extend(distill_move_edit((refactor_obj)))
        # return ret
        ret = {}
        for refactor_obj in refactor_objs:
            moves = cls.distill_move_edit(refactor_obj)
            for move in moves:
                try:
                    ret[move.to_state.get_category() + move.to_state.longname()].append(move)
                except KeyError:
                    ret[move.to_state.get_category() + move.to_state.longname()] = []
                    ret[move.to_state.get_category() + move.to_state.longname()].append(move)
        return ret

    @classmethod
    def distill_move_edit(cls, refactor_obj: dict) -> List[MoveEdit]:
        refactor_kind = refactor_obj["type"]
        description = refactor_obj["description"]
        if refactor_kind not in MoveMethodRefactorings + MoveClassRefactoring + MoveParamRefactorings:
            return []
        states = extract_state(refactor_kind,
                               description,
                               refactor_obj["leftSideLocations"],
                               refactor_obj["rightSideLocations"])
        ret = []
        for state in states:
            ret.append(MoveEdit(state[0], state[1], refactor_obj))
        # for src in src_states:
        #     for to in to_states:
        #         ret.append(MoveEdit(src, to, refactor_obj))

        return ret

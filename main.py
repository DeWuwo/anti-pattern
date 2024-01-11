import argparse
from utils import FileJson, FileCSV, Constant
from model.build_model import BuildModel
# from model.anti_pattern import AntiPattern
# from model.coupling_pattern import CouplingPattern
from model.patterns.coupling_patterns import CouplingPattern
from model.match import Match
from model.generate_history import GenerateHistory
from model.mc.mc import MC

access_map = {'': '0', 'Private': '1', 'Protected': '2', 'Public': '3'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo_extensive', '-rpe', action='store', dest='repo_extensive',
                        help='code path of honor')
    parser.add_argument('--repo_aosp', '-rpa', action='store', dest='repo_aosp',
                        help='code path of android')
    parser.add_argument('--rel_extensive', '-rele', action='store', dest='rel_extensive',
                        help='root json file of honor')
    parser.add_argument('--rel_aosp', '-rela', action='store', dest='rel_aosp',
                        help='root json file of android')
    parser.add_argument('--commit_extensive', '-ce', action='store', dest='commit_extensive',
                        help='commit of honor')
    parser.add_argument('--commit_aosp', '-ca', action='store', dest='commit_aosp',
                        help='commit of android')
    parser.add_argument('--refactor_miner', '-ref', action='store', dest='refactor_miner',
                        help='root directory of refactor miner tool')
    parser.add_argument('--output', '-o', action='store', dest='output',
                        help='root directory of out')
    args = parser.parse_args()
    dispatch(args)


def dispatch(args):
    if args.repo_extensive is None:
        raise ValueError("repo_extensive directory of project must supply")
    if args.repo_aosp is None:
        raise ValueError("repo_aosp directory of project must supply")
    if args.rel_extensive is None:
        raise ValueError("extensive relation file must supply")
    if args.rel_aosp is None:
        raise ValueError("aosp relation file must supply")
    if args.commit_extensive is None:
        raise ValueError("extensive commit must supply")
    if args.commit_aosp is None:
        raise ValueError("aosp commit must supply")
    if args.output is None:
        raise ValueError("output path must supply")
    # read files
    try:
        repo_extensive = args.repo_extensive
        repo_aosp = args.repo_aosp
        rel_extensive = args.rel_extensive
        rel_aosp = args.rel_aosp
        commit_extensive = args.commit_extensive
        commit_aosp = args.commit_aosp
        ref_path = args.refactor_miner
        out_path = args.output

        Constant.load_core_files('core_files.txt')
        Constant.load_module_files('module_files.txt')
        entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
            FileJson.read_from_json(rel_aosp, rel_extensive)
        # 读取模块责任田
        module_blame = out_path

        # build base model
        gen_history = GenerateHistory(repo_aosp, repo_extensive, commit_aosp, commit_extensive,
                                      rel_extensive, ref_path, out_path)

        base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                                entities_stat_aosp, gen_history, out_path)

        mc = MC(out_path, repo_extensive, list(base_model.file_set_extension), repo_aosp,
                list(base_model.file_set_android))
        mc.get_mc()
        pattern_match = Match(base_model, out_path, module_blame, repo_extensive)
        # match coupling pattern
        coupling_pattern = CouplingPattern()
        pattern_match.start_match_pattern(coupling_pattern)

        # match anti pattern
        # special_anti_pattern = AntiPattern()
        # pattern_match.start_match_pattern(special_anti_pattern)
    except FileNotFoundError as e:
        print(e)


def test():
    try:
        repo_extensive = "D:\\Honor\\source_code\\LineageOS\\base"
        repo_aosp = "D:\\Honor\\source_code\\android\\base"
        rel_extensive = "D:\\Honor\\dep_res\\LineageOS\\base\\7f7fc2562a95be630dbe609e8fb70383dcfada4f.json"
        rel_aosp = "D:\\Honor\\dep_res\\android\\base\\49d8b986dddd441df741698541788c5f3a9c465f.json"
        commit_extensive = "7f7fc2562a95be630dbe609e8fb70383dcfada4f"
        commit_aosp = "49d8b986dddd441df741698541788c5f3a9c465f"
        ref_path = 'E:\\Graduate\\RefactoringMine\\utils\\bin'
        out_path = "D:\\Honor\\match_res\\LineageOS\\base\\lineage-18.1"

        Constant.load_core_files('core_files.txt')
        Constant.load_module_files('module_files.txt')
        entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
            FileJson.read_from_json(rel_aosp, rel_extensive)
        # 读取模块责任田
        module_blame = out_path

        # build base model
        gen_history = GenerateHistory(repo_aosp, repo_extensive, commit_aosp, commit_extensive,
                                      rel_extensive, ref_path, out_path)

        base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                                entities_stat_aosp, gen_history, out_path)

        mc = MC(out_path, repo_extensive, list(base_model.file_set_extension), repo_aosp,
                list(base_model.file_set_android))
        mc.get_mc()
        pattern_match = Match(base_model, out_path, module_blame, repo_extensive)
        # match coupling pattern
        coupling_pattern = CouplingPattern()
        pattern_match.start_match_pattern(coupling_pattern)

        # match anti pattern
        # special_anti_pattern = AntiPattern()
        # pattern_match.start_match_pattern(special_anti_pattern)
    except FileNotFoundError as e:
        print(e)


if __name__ == '__main__':
    main()
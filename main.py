import argparse
from utils import FileJson, FileCSV, Constant
from model.build_model import BuildModel
from model.anti_pattern import AntiPattern
from model.coupling_pattern import CouplingPattern
from model.match import Match

access_map = {'': '0', 'Private': '1', 'Protected': '2', 'Public': '3'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--honor', '-c', action='store', dest='honor',
                        help='root json file of honor')
    parser.add_argument('--android', '-a', action='store', dest='android',
                        help='root json file of android')
    parser.add_argument('--output', '-o', action='store', dest='output',
                        help='root directory of out')
    args = parser.parse_args()
    dispatch(args)


def dispatch(args):
    if not hasattr(args, 'honor'):
        raise ValueError("root directory of project must supply")

    if args.honor is None:
        raise ValueError("root directory of project must supply")
    if args.android is None:
        raise ValueError("root directory of project must supply")
    if args.output is None:
        raise ValueError("root directory of project must supply")
    # read files
    try:
        entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
            FileJson.read_from_json(args.android, args.honor)
        # intrusive_entities = FileCSV.read_from_csv(
        #     'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_mixed_entities.csv')
        # assi_entities = FileCSV.read_from_csv(
        #     'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_pure_third_party_entities.csv')
        # commit_null_entities = FileCSV.read_from_csv(
        #     'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_all_entities.csv')
        # build base model
        base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                                entities_stat_aosp, [], [], [])
        pattern_match = Match(base_model, args.output)
        # match coupling pattern
        coupling_pattern = CouplingPattern()
        pattern_match.start_match_pattern(coupling_pattern)

        # match anti pattern
        special_anti_pattern = AntiPattern()
        pattern_match.start_match_pattern(special_anti_pattern)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()

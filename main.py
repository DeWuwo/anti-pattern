import argparse
import os
from datetime import date
from utils import FileReader
from model.build_model import BuildModel
from model.anti_pattern import AntiPattern
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
    entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp, entities_stat_aosp = \
        FileReader().read_from_json(args.android, args.honor)
    intrusive_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_mixed_entities.csv')
    assi_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_pure_third_party_entities.csv')
    commit_null_entities = FileReader.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_all_entities.csv')
    # build base model
    base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                            entities_stat_aosp, intrusive_entities, assi_entities, commit_null_entities)
    pattern_match = AntiPattern(Match(base_model))
    # match and output
    match_set_stat, match_set, union_temp, anti_patterns = pattern_match.start_detect_coupling()
    # match coupling pattern
    coupling_path = os.path.join(args.output + 'coupling')
    FileReader.write_match_mode(coupling_path, match_set)
    FileReader.write_to_json(coupling_path, union_temp, 1)
    FileReader.write_to_json(coupling_path, anti_patterns, 3)
    FileReader.write_to_json(coupling_path, match_set_stat, 4)
    FileReader.write_to_csv(coupling_path, date.today(), args.honor, args.android, match_set_stat)

    # match anti pattern
    anti_path = os.path.join(args.output + 'anti-pattern')
    match_set_stat, match_set, union_temp, anti_patterns = pattern_match.start_detect_anti_patterns()
    FileReader.write_match_mode(anti_path, match_set)
    FileReader.write_to_json(anti_path, union_temp, 1)
    FileReader.write_to_json(anti_path, anti_patterns, 3)
    FileReader.write_to_json(anti_path, match_set_stat, 4)
    FileReader.write_to_csv(anti_path, date.today(), args.honor, args.android, match_set_stat)


if __name__ == '__main__':
    main()

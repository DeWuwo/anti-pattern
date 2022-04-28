import argparse
from utils import FileJson, FileCSV, Constant
from model.build_model import BuildModel
from model.pattern_type import PatternType
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
        FileJson.read_from_json(args.android, args.honor)
    intrusive_entities = FileCSV.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_mixed_entities.csv')
    assi_entities = FileCSV.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_pure_third_party_entities.csv')
    commit_null_entities = FileCSV.read_from_csv(
        'D:/Honor/experiment/lineage/4-18/base/blame/lineageos_all_entities.csv')
    # build base model
    base_model = BuildModel(entities_honor, cells_honor, entities_stat_honor, entities_aosp, cells_aosp,
                            entities_stat_aosp, intrusive_entities, assi_entities, commit_null_entities)
    pattern_match = Match(base_model, args.output)
    # match coupling pattern
    coupling_pattern = PatternType('coupling-patterns',
                                   ['Android2Honor/InheritClassCouplingDep', 'Android2Honor/ImplementClassCouplingDep',
                                    'Android2Honor/AggregationExtensionInterfaceClassDep',
                                    'Android2Honor/ParameterListModifyDep',
                                    'Honor2Android/InheritanceUseParentProtected',
                                    'Honor2Android/AggregationAOSPClassDep',
                                    'Honor2Android/InnerExtensionClassUseDep',
                                    'Honor2Android/EncapsulationAOSPInterface',
                                    'Honor2Android/PublicInterfaceUseDep'],
                                   [
                                       {
                                           'Android2Honor/InheritClassCouplingDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class,
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.inherit,
                                                       'dest': {'id': [-1], 'category': Constant.E_class,
                                                                'attrs': {'accessible': []}},
                                                       'direction': '01'
                                                   }]
                                           ]
                                       },
                                       {
                                           'Android2Honor/ImplementClassCouplingDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class,
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.implement,
                                                       'dest': {'id': [-1], 'category': Constant.E_interface,
                                                                'attrs': {'accessible': []}},
                                                       'direction': '01'
                                                   }]
                                           ]
                                       },
                                       {
                                           'Android2Honor/AggregationExtensionInterfaceClassDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '01'
                                                   },
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_interface,
                                                               'attrs': {}},
                                                       'rel': Constant.typed,
                                                       'dest': {'id': ['id', 0, 1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'rel': Constant.implement,
                                                       'dest': {'id': ['id', 1, 0], 'category': Constant.E_interface,
                                                                'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 2, 0], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': ['id', 3, 1], 'category': Constant.E_method,
                                                                'attrs': {}},
                                                       'direction': '01'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['id', 4, 0], 'category': Constant.E_method,
                                                                'attrs': {}},
                                                       'direction': '00'
                                                   }
                                               ]

                                           ]
                                       },
                                       {
                                           'Android2Honor/ParameterListModifyDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'rel': Constant.param,
                                                       'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '01'
                                                   }
                                               ]
                                           ]
                                       },
                                       {
                                           'Honor2Android/InheritanceUseParentProtected': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': 'Class',
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.inherit,
                                                       'dest': {'id': [-1], 'category': 'Class',
                                                                'attrs': {'accessible': []}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 0], 'category': 'Class',
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': 'Method',
                                                                'attrs': {'accessible': []}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 1, 1], 'category': 'Method',
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': [-1], 'category': 'Method',
                                                                'attrs': {'accessible': ['protected']}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 1], 'category': 'Class',
                                                               'attrs': {'accessible': []}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['id', 2, 1], 'category': 'Method',
                                                                'attrs': {'accessible': ['protected']}},
                                                       'direction': '00'
                                                   }
                                               ]
                                           ]
                                       },
                                       {
                                           'Honor2Android/AggregationAOSPClassDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                                               'attrs': {}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 2, 1], 'category': Constant.E_variable,
                                                               'attrs': {}},
                                                       'rel': Constant.typed,
                                                       'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 3, 1], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                                                'attrs': {}},
                                                       'direction': '00'
                                                   },
                                               ]
                                           ]
                                       },
                                       {
                                           'Honor2Android/InnerExtensionClassUseDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'direction': '01'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 1], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                                               'attrs': {}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['id', 2, 1], 'category': Constant.E_method,
                                                                'attrs': {}},
                                                       'direction': '00'
                                                   },
                                               ]

                                           ]
                                       },
                                       {
                                           'Honor2Android/EncapsulationAOSPInterface': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '11'
                                                   },
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_interface,
                                                               'attrs': {}},
                                                       'rel': Constant.typed,
                                                       'dest': {'id': ['id', 1, 1], 'category': Constant.E_variable,
                                                                'attrs': {}},
                                                       'direction': '01'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                                               'attrs': {}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'direction': '10'
                                                   },
                                                   {
                                                       'src': {'id': ['id', 2, 0], 'category': Constant.E_interface,
                                                               'attrs': {}},
                                                       'rel': Constant.define,
                                                       'dest': {'id': ['id', 3, 1], 'category': Constant.E_method,
                                                                'attrs': {}},
                                                       'direction': '00'
                                                   },
                                               ]
                                           ]
                                       },
                                       {
                                           'Honor2Android/PublicInterfaceUseDep': [
                                               [
                                                   {
                                                       'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                                                       'rel': Constant.call,
                                                       'dest': {'id': [-1], 'category': Constant.E_method,
                                                                'attrs': {'accessible': ['public', '']}},
                                                       'direction': '10'
                                                   },
                                               ]
                                           ]
                                       }
                                   ])
    pattern_match.start_match_pattern(coupling_pattern)

    # match anti pattern
    special_anti_pattern = PatternType('anti-patterns', ['FinalDel', 'ClassAccessibility', 'HiddenApi', 'HiddenModify',
                                                         'ParamListModify',
                                                         'InheritDestroy'], [
                                           {
                                               'FinalDel': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_class,
                                                                   'attrs': {}},
                                                           'rel': Constant.inherit,
                                                           'dest': {'id': [-1], 'category': Constant.E_class,
                                                                    'attrs': {'final': True}},
                                                           'direction': '10'
                                                       }
                                                   ],
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {}},
                                                           'rel': Constant.override,
                                                           'dest': {'id': [-1], 'category': Constant.E_method,
                                                                    'attrs': {'final': True}},
                                                           'direction': '10'
                                                       },
                                                   ]
                                               ]
                                           },
                                           {
                                               'ClassAccessibility': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_class,
                                                                   'attrs': {}},
                                                           'rel': Constant.define,
                                                           'dest': {'id': [-1], 'category': Constant.E_class,
                                                                    'attrs': {'accessible_modify': True}},
                                                           'direction': '00'
                                                       }
                                                   ]
                                               ]
                                           },
                                           {
                                               'HiddenApi': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {}},
                                                           'rel': Constant.call,
                                                           'dest': {'id': [-1], 'category': Constant.E_method,
                                                                    'attrs': {'hidden': True}},
                                                           'direction': '10'
                                                       }
                                                   ],
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {}},
                                                           'rel': Constant.use,
                                                           'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                    'attrs': {'hidden': True}},
                                                           'direction': '10'
                                                       }

                                                   ]
                                               ]
                                           },
                                           {
                                               'HiddenModify': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {}},
                                                           'rel': Constant.call,
                                                           'dest': {'id': [-1], 'category': Constant.E_method,
                                                                    'attrs': {'hidden_modify': True}},
                                                           'direction': '10'
                                                       }
                                                   ],
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {}},
                                                           'rel': Constant.use,
                                                           'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                    'attrs': {'hidden_modify': True}},
                                                           'direction': '10'
                                                       }

                                                   ]
                                               ]
                                           },
                                           {
                                               'ParamListModify': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_method,
                                                                   'attrs': {'accessible': ['public']}},
                                                           'rel': Constant.param,
                                                           'dest': {'id': [-1], 'category': Constant.E_variable,
                                                                    'attrs': {}},
                                                           'direction': '01'
                                                       }
                                                   ]
                                               ]
                                           },
                                           {
                                               'InheritDestroy': [
                                                   [
                                                       {
                                                           'src': {'id': [-1], 'category': Constant.E_class,
                                                                   'attrs': {}},
                                                           'rel': Constant.inherit,
                                                           'dest': {'id': [-1], 'category': Constant.E_class,
                                                                    'attrs': {}},
                                                           'direction': '01'
                                                       }
                                                   ]
                                               ]
                                           }
                                       ])
    pattern_match.start_match_pattern(special_anti_pattern)


if __name__ == '__main__':
    main()

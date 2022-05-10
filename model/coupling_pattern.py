from model.pattern_type import PatternType
from utils import Constant


class CouplingPattern(PatternType):
    def __init__(self):
        ident = 'coupling-patterns'
        patterns = ['Android2Honor/InheritClassCouplingDep',
                    'Android2Honor/ImplementClassCouplingDep',
                    'Android2Honor/AggregationExtensionInterfaceClassDep',
                    'Android2Honor/ParameterListModifyDep',
                    'Honor2Android/InheritanceUseParentProtected',
                    'Honor2Android/AggregationAOSPClassDep',
                    'Honor2Android/InnerExtensionClassUseDep',
                    'Honor2Android/EncapsulationAOSPInterface',
                    'Honor2Android/PublicInterfaceUseDep']
        rules = [
            {
                patterns[0]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'accessible': []}},
                            'direction': '01'
                        }]
                ]
            },
            {
                patterns[1]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.implement, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_interface,
                                     'attrs': {'accessible': []}},
                            'direction': '01'
                        }]
                ]
            },
            {
                patterns[2]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '01'
                        },
                        {
                            'src': {'id': [-1], 'category': Constant.E_interface,
                                    'attrs': {}},
                            'rel': {'type': Constant.typed, 'attrs': {}},
                            'dest': {'id': ['id', 0, 1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.implement, 'attrs': {}},
                            'dest': {'id': ['id', 1, 0], 'category': Constant.E_interface,
                                     'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 2, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': ['id', 3, 1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '01'
                        },
                        {
                            'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 4, 0], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '00'
                        }
                    ]

                ]
            },
            {
                patterns[3]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.param, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '01'
                        }
                    ]
                ]
            },
            {
                patterns[4]: [
                    [
                        {
                            'src': {'id': [-1], 'category': 'Class',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': 'Class',
                                     'attrs': {'accessible': []}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 0], 'category': 'Class',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': 'Method',
                                     'attrs': {'accessible': []}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 1, 1], 'category': 'Method',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': 'Method',
                                     'attrs': {'accessible': ['protected']}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': 'Class',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 2, 1], 'category': 'Method',
                                     'attrs': {'accessible': ['protected']}},
                            'direction': '00'
                        }
                    ]
                ]
            },
            {
                patterns[5]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 2, 1], 'category': Constant.E_variable,
                                    'attrs': {}},
                            'rel': {'type': Constant.typed, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 3, 1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '00'
                        },
                    ]
                ]
            },
            {
                patterns[6]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'direction': '01'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 2, 1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '00'
                        },
                    ]

                ]
            },
            {
                patterns[7]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': [-1], 'category': Constant.E_interface,
                                    'attrs': {}},
                            'rel': {'type': Constant.typed, 'attrs': {}},
                            'dest': {'id': ['id', 1, 1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '01'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 2, 0], 'category': Constant.E_interface,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 3, 1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '00'
                        },
                    ]
                ]
            },
            {
                patterns[8]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'accessible': [Constant.accessible_list[2], '']}},
                            'direction': '10'
                        },
                    ]
                ]
            }
        ]

        PatternType.__init__(self, ident, patterns, rules)

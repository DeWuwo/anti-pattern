from model.pattern_type import PatternType
from utils import Constant


class CouplingPattern(PatternType):
    def __init__(self):
        ident = 'coupling-patterns'
        patterns = ['Android2Honor/InheritClassCouplingDep',
                    'Android2Honor/ImplementClassCouplingDep',
                    'Android2Honor/AggregationExtensionInterfaceClassDep',
                    'Android2Honor/ParameterListModifyDep',
                    'Honor2Android/InnerExtensionClassUseDep',
                    'Honor2Android/InheritanceUseParentProtected',
                    'Honor2Android/AggregationAOSPClassDep',
                    'Honor2Android/EncapsulationAOSPInterface',
                    'Honor2Android/PublicInterfaceUseDep',
                    'Honor2Android/ReflectUse']
        rules = [
            {
                'Android2Honor/InheritClassCouplingDep': [
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
                'Android2Honor/ImplementClassCouplingDep': [
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
                'Android2Honor/AggregationExtensionInterfaceClassDep': [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '00'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '01'
                        },
                        # {
                        #     'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        #     'rel': {'type': Constant.implement, 'attrs': {}},
                        #     'dest': {'id': ['id', 1, 0], 'category': Constant.E_interface,
                        #              'attrs': {}},
                        #     'direction': '11'
                        # },
                        {
                            'src': {'id': ['id', 0, 0], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['bindVar', 1], 'category': Constant.E_variable, 'attrs': {}},
                            'direction': '01'
                        },
                        {
                            'src': {'id': ['id', 2, 1], 'category': Constant.E_variable, 'attrs': {}},
                            'rel': {'type': Constant.typed, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_interface,
                                     'attrs': {}},
                            'direction': '11'
                        },
                        {
                            'src': {'id': ['id', 3, 1], 'category': Constant.E_interface,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                     'attrs': {}},
                            'direction': '11'
                        }
                    ]

                ]
            },
            {
                'Android2Honor/ParameterListModifyDep': [
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
                'Honor2Android/InnerExtensionClassUseDep': [
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
                'Honor2Android/InheritanceUseParentProtected': [
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
                                     'attrs': {'accessible': ['protected', '']}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 0, 1], 'category': 'Class',
                                    'attrs': {'accessible': []}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': ['id', 2, 1], 'category': 'Method',
                                     'attrs': {'accessible': ['protected', '']}},
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
                'Honor2Android/EncapsulationAOSPInterface': [
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
                            'dest': {'id': [-1], 'category': Constant.E_interface, 'attrs': {}},
                            'direction': '10'
                        },
                        {
                            'src': {'id': ['id', 3, 1], 'category': Constant.E_interface,
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
                'Honor2Android/PublicInterfaceUseDep': [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[2]], 'accessible_modify': False}
                                     },
                            'direction': '10'
                        },
                    ]
                ]
            },
            {
                'Honor2Android/ReflectUse': [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '00'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                            'rel': {'type': Constant.reflect, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                            'direction': '00'
                        }
                    ]
                ]
            }
        ]

        PatternType.__init__(self, ident, patterns, rules)

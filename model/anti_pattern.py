from model.pattern import Pattern
from model.match import Match
from utils import Constant


class AntiPattern(Pattern):
    anti_patterns = [
        {},
        {
            'Android2Honor/InheritClassCouplingDep': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}},
                        'rel': Constant.inherit,
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}},
                        'direction': '01'
                    }]
            ]
        },
        {
            'Android2Honor/ImplementClassCouplingDep': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}},
                        'rel': Constant.implement,
                        'dest': {'id': [-1], 'category': Constant.E_interface, 'attrs': {'accessible': []}},
                        'direction': '10'
                    }]
            ]
        },
        {
            'Android2Honor/AggregationExtensionInterfaceClassDep': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'intrusive': True}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': [-1], 'category': Constant.E_interface, 'attrs': {}},
                        'rel': Constant.typed,
                        'dest': {'id': ['id', 0, 1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.implement,
                        'dest': {'id': ['id', 1, 0], 'category': Constant.E_interface, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 2, 0], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.call,
                        'dest': {'id': ['id', 3, 1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': ['id', 4, 0], 'category': Constant.E_method, 'attrs': {}},
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
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    }
                ]
            ]
        },
        {
            'Honor2Android/InheritanceUseParentProtected': [
                [
                    {
                        'src': {'id': [-1], 'category': 'Class', 'attrs': {'accessible': []}},
                        'rel': Constant.inherit,
                        'dest': {'id': [-1], 'category': 'Class', 'attrs': {'accessible': []}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': 'Class', 'attrs': {'accessible': []}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': 'Method', 'attrs': {'accessible': []}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 1, 1], 'category': 'Method', 'attrs': {'accessible': []}},
                        'rel': Constant.call,
                        'dest': {'id': [-1], 'category': 'Method', 'attrs': {'accessible': ['protected']}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': 'Class', 'attrs': {'accessible': []}},
                        'rel': Constant.define,
                        'dest': {'id': ['id', 2, 1], 'category': 'Method', 'attrs': {'accessible': ['protected']}},
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
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.call,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.typed,
                        'dest': {'id': ['id', 2, 1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 3, 0], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method, 'attrs': {}},
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
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 1, 1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.call,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 2, 1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': ['id', 0, 0], 'category': Constant.E_method, 'attrs': {}},
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
                        'src': {'id': ['id', 0, 0], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': [-1], 'category': Constant.E_interface, 'attrs': {}},
                        'rel': Constant.typed,
                        'dest': {'id': ['id', 2, 1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    },
                    {
                        'src': {'id': ['id', 0, 1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.call,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'direction': '10'
                    },
                    {
                        'src': {'id': ['id', 2, 0], 'category': Constant.E_interface, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': ['id', 3, 1], 'category': Constant.E_method, 'attrs': {}},
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
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {'accessible': ['public']}},
                        'direction': '10'
                    },
                ]
            ]
        }
    ]

    special_anti_patterns = [
        {
            'FinalDel': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.inherit,
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'intrusive': True, 'final': True}},
                        'direction': '10'
                    },
                ],
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.override,
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'intrusive': True, 'final': True}},
                        'direction': '10'
                    },
                ]
            ]
        },
        {
            'ClassAccessibility': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                        'rel': Constant.define,
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible_modify': True}},
                        'direction': '00'
                    }
                ]
            ]
        },
        {
            'HiddenApi': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.call,
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {'hidden': True}},
                        'direction': '10'
                    }
                ],
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': Constant.use,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {'hidden': True}},
                        'direction': '10'
                    }

                ]
            ]
        },
        {
            'ParamListModify': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {'accessible': ['public']}},
                        'rel': Constant.param,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    }
                ]
            ]
        },
        {
            'InheritDestroy': [
                [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {'intrusive': True}},
                        'rel': Constant.inherit,
                        'dest': {'id': [-1], 'category': Constant.E_variable, 'attrs': {}},
                        'direction': '01'
                    }
                ]
            ]
        }
    ]

    def __init__(self, match: Match):
        Pattern.__init__(self, match)

    def start_detect(self):
        print('start detect anti pattern ')
        return self.matchPattern(self.anti_patterns)

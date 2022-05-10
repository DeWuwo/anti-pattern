from model.pattern_type import PatternType
from utils import Constant


class AntiPattern(PatternType):
    def __init__(self):
        ident = 'anti-patterns'
        patterns = ['FinalDel', 'ClassAccessibility', 'HiddenApi', 'HiddenModify',
                    'ParamListModify',
                    'InheritDestroy', 'Reflect']
        rules = [
            {
                patterns[0]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'final': True}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.override, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'final': True}},
                            'direction': '10'
                        },
                    ]
                ]
            },
            {
                patterns[1]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.define, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {'accessible_modify': True}},
                            'direction': '00'
                        }
                    ]
                ]
            },
            {
                patterns[2]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'hidden': True}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.use, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {'hidden': True}},
                            'direction': '10'
                        }

                    ]
                ]
            },
            {
                patterns[3]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.call, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {'hidden_modify': True}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.use, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {'hidden_modify': True}},
                            'direction': '10'
                        }

                    ]
                ]
            },
            {
                patterns[4]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {'accessible': ['public']}},
                            'rel': {'type': Constant.param, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_variable,
                                     'attrs': {}},
                            'direction': '01'
                        }
                    ]
                ]
            },
            {
                patterns[5]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.inherit, 'attrs': {}},
                            'dest': {'id': [-1], 'category': Constant.E_class,
                                     'attrs': {}},
                            'direction': '01'
                        }
                    ]
                ]
            },
            {
                patterns[6]: [
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_method,
                                    'attrs': {}},
                            'rel': {'type': Constant.reflect,
                                    'attrs': {'set_accessible': True,
                                              'invoke': True}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[0], Constant.accessible_list[1]]}},
                            'direction': '10'
                        }
                    ],
                    [
                        {
                            'src': {'id': [-1], 'category': Constant.E_class,
                                    'attrs': {}},
                            'rel': {'type': Constant.reflect,
                                    'attrs': {'set_accessible': True,
                                              'invoke': True}},
                            'dest': {'id': [-1], 'category': Constant.E_method,
                                     'attrs': {
                                         'accessible': [Constant.accessible_list[0], Constant.accessible_list[1]]}},
                            'direction': '10'
                        }
                    ]
                ]
            }
        ]
        PatternType.__init__(self, ident, patterns, rules)

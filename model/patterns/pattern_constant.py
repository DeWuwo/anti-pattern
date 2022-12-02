from model.patterns.pattern_rules import PatternRules
from utils import Constant
from model.metric.metric_constant import MetricCons

filter_list = ['android.util', 'android.os.Message', 'com.android.internal.logging',
               'com.android.internal.os', 'android.os', 'com.android.server.utils',
               'hihonor.android.utils', 'android.os.ServiceManager', 'com.android.server.LocalServices',
               'android.provider.Settings.Secure', 'android.provider.Settings.System',
               'com.android.telephony.Rlog']


class PatternCons:
    pattern_final = PatternRules(
        'FinalDel',
        [1, 0], [0], {
            'del_class_final_for_inherit': {
                'metrics': {MetricCons.Me_is_inherit: [0, 1], MetricCons.Me_stability: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_file,
                                'attrs': {}},
                        'rel': {'type': Constant.contain, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    }
                ]
            },
            'del_method_final_for_override': {
                'metrics': {MetricCons.Me_is_override: [0, 1], MetricCons.Me_stability: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]},
            'del_class_final_for_var': {
                'metrics': {MetricCons.Me_interface_number: [0, 0]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'final': True, 'intrusive': True}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]
            },
            'del_class_final_for_method': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'final': True, 'intrusive': True}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]
            },
            'del_method_final_for_var': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {'final': True, 'intrusive': True}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {'final': True, 'intrusive': True}},
                        'direction': '00'
                    },
                ]
            }
        })

    pattern_access = PatternRules('AccessibilityModify', [], [], {
        'class_access_modify': {
            'metrics': {MetricCons.Me_native_used_frequency: [0, 1], MetricCons.Me_stability: [0, 1]},
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_class,
                             'attrs': {'accessible_up': True, 'intrusive': True},
                             'filter': {'qualified_name': filter_list}},
                    'direction': '00'
                }
            ]
        },
        'method_access_modify': {
            'metrics': {MetricCons.Me_native_used_frequency: [0, 1], MetricCons.Me_native_used_effectiveness: [0, 1],
                        MetricCons.Me_stability: [0, 1]},
            'rules': [
                {
                    'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {}},
                    'rel': {'type': Constant.define, 'attrs': {}},
                    'dest': {'id': [-1], 'category': Constant.E_method,
                             'attrs': {'accessible_up': True, 'intrusive': True},
                             'filter': {'qualified_name': filter_list}},
                    'direction': '00'
                },
            ]
        }
    })

    pattern_hidden = PatternRules(
        'HiddenApi', [1, 0], [0], {
            'call_method': {
                'metrics': {MetricCons.Me_acceptable_hidden: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'hidden': [Constant.HD_blacklist,
                                                      Constant.HD_greylist] + Constant.HD_greylist_max_list},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }
                ]},
            'use_variable': {
                'metrics': {MetricCons.Me_acceptable_hidden: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.use, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {'hidden': [Constant.HD_blacklist,
                                                      Constant.HD_greylist] + Constant.HD_greylist_max_list},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }

                ]
            },
            'call_special_hidden': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method,
                                'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {'hidden': [Constant.HD_hidden]},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }

                ]
            }
        })

    pattern_param_modify = PatternRules(
        'ParameterListModifyDep', [1, 0], [0], {
            'add_parameter': {
                'metrics': {MetricCons.Me_add_param: [0, 1], MetricCons.Me_native_used_frequency: [0, 0]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {'intrusive': True},
                                'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.param, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_variable,
                                 'attrs': {}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_inner_class = PatternRules(
        'InnerExtensionClassUseDep',
        [1, 1, 0, 0, 0, 0, 0, 0], [1, 2, 3], {
            'inner_class': {
                'metrics': {MetricCons.Me_inner_scale: [0, 1], MetricCons.Me_extensive_access_frequency: [2, 1],
                            MetricCons.Me_anonymous_class: [0, 1], MetricCons.Me_stability: [0, 0]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class, 'attrs': {},
                                'filter': {'qualified_name': filter_list}},
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
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {'accessible': [Constant.accessible_list[2]]}},
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
            }
        }
    )

    pattern_inherit_extensive = PatternRules(
        'InheritExtension', [1, 0], [0], {
            'inherit_extensive_class': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.inherit, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {'accessible': []}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_implement_extensive = PatternRules(
        'ImplementExtension', [1, 0], [0], {
            'implement_extensive_interface': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                        'rel': {'type': Constant.implement, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface,
                                 'attrs': {'accessible': []}},
                        'direction': '01'
                    }
                ]
            }
        }
    )

    pattern_aggre_extensive = PatternRules(
        'AggregationExtensionInterfaceClassDep',
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4], {
            'aggregate_interface': {
                'metrics': {MetricCons.Me_stability: [0, 1], MetricCons.Me_native_access_frequency: [1, 1]},
                'rules': [
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
                                 'attrs': {}, 'filter': {'qualified_name': filter_list}},
                        'direction': '01'
                    },
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
                ]},
            'aggregate_class': {
                'metrics': {MetricCons.Me_stability: [0, 1],
                            MetricCons.Me_native_access_frequency: [1, 1]},
                'rules': [
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
                                 'attrs': {}, 'filter': {'qualified_name': filter_list}},
                        'direction': '01'
                    },
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
                        'dest': {'id': [-1], 'category': Constant.E_class,
                                 'attrs': {}},
                        'direction': '11'
                    },
                    {
                        'src': {'id': ['id', 3, 1], 'category': Constant.E_class,
                                'attrs': {}},
                        'rel': {'type': Constant.define, 'attrs': {}},
                        'dest': {'id': ['id', 1, 1], 'category': Constant.E_method,
                                 'attrs': {}},
                        'direction': '11'
                    }
                ]
            }
        }
    )

    pattern_inherit_native = PatternRules(
        'InheritanceNative',
        [1, 1, 1, 1, 1, 0, 1, 0], [2, 3], {
            'inherit_native_class': {
                'metrics': {},
                'rules': [
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
                                 'attrs': {'accessible': ['protected', '']},
                                 'filter': {'qualified_name': filter_list}},
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
            }
        }
    )

    pattern_implement_native = PatternRules(
        'ImplementNative', [1, 0], [0], {
            'implement_native_interface': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_class,
                                'attrs': {'accessible': []}},
                        'rel': {'type': Constant.implement, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_interface,
                                 'attrs': {'accessible': []}, 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }]
            }
        }
    )

    pattern_aggre_native = PatternRules(
        'AggregationAOSPClassDep',
        [1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [1, 4], {
            'aggregate_interface': {
                'metrics': {},
                'rules': [
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
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {'qualified_name': filter_list}},
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
                ]},
            'aggregate_class': {
                'metrics': {},
                'rules': [
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
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {'qualified_name': filter_list}},
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
                ],
            }
        }
    )

    pattern_public_interface = PatternRules(
        'PublicInterfaceUseDep', [1, 0], [0], {
            'call_public': {
                'metrics': {},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.call, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method,
                                 'attrs': {
                                     'accessible': [Constant.accessible_list[2]], 'accessible_modify': False},
                                 'filter': {'qualified_name': filter_list}
                                 },
                        'direction': '10'
                    },
                ]
            }
        }
    )

    pattern_reflect = PatternRules(
        'ReflectUse', [1, 0], [0], {
            'reflect_method': {
                'metrics': {MetricCons.Me_module: [0, 0], MetricCons.Me_extensive_access_frequency: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.reflect, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_method, 'attrs': {},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }
                ]},
            'reflect_class': {
                'metrics': {MetricCons.Me_module: [0, 0], MetricCons.Me_extensive_access_frequency: [0, 1]},
                'rules': [
                    {
                        'src': {'id': [-1], 'category': Constant.E_method, 'attrs': {}},
                        'rel': {'type': Constant.reflect, 'attrs': {}},
                        'dest': {'id': [-1], 'category': Constant.E_class, 'attrs': {},
                                 'filter': {'qualified_name': filter_list}},
                        'direction': '10'
                    }
                ],
            }
        }
    )

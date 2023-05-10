from model.patterns.pattern_type import PatternType
from model.patterns.pattern_constant import PatternCons


class CouplingPattern(PatternType):
    def __init__(self):
        ident = 'coupling-patterns'
        patterns = ['FinalDel', 'AccessibilityModify',
                    'HiddenApi',
                    'ParameterListModifyDep',
                    'InnerExtensionClassUseDep',
                    'InheritExtension',
                    'ImplementExtension',
                    'AggregationExtensionInterfaceClassDep',

                    'InheritanceNative',
                    'ImplementNative',
                    'AggregationAOSPClassDep',
                    'PublicInterfaceUseDep',
                    'ReflectUse']
        styles = ['native_class_intrusive_add_method', 'native_method_intrusive', 'del_native_class_final',
                  'del_native_method_final', 'del_native_class_final_for_var',
                  'del_native_class_final_for_inherit_and_override',
                  'native_class_access_modify', 'native_method_access_modify', 'call_native_hidden_method',
                  'use_native_hidden_variable', 'native_method_add_parameter', 'native_class_add_inner_class',
                  'native_class_inherit_extensive_class', 'native_class_implement_extensive_interface',
                  'native_class_aggregate_extensive_interface', 'native_class_aggregate_extensive_class',
                  'extensive_class_inherit_native_class', 'extensive_class_implement_native_interface',
                  'extensive_class_aggregate_native_interface', 'extensive_class_aggregate_native_class',
                  'extensive_method_call_native_public_method', 'extensive_method_reflect_native_method',
                  'extensive_method_reflect_native_class']
        rules = [PatternCons.pattern_final, PatternCons.pattern_access, PatternCons.pattern_hidden,
                 PatternCons.pattern_param_modify, PatternCons.pattern_inner_class,
                 PatternCons.pattern_inherit_extensive, PatternCons.pattern_implement_extensive,
                 PatternCons.pattern_aggre_extensive,
                 PatternCons.pattern_inherit_native,
                 PatternCons.pattern_implement_native, PatternCons.pattern_aggre_native,
                 PatternCons.pattern_public_interface, PatternCons.pattern_reflect]

        PatternType.__init__(self, ident, patterns, styles, rules)

from model.patterns.pattern_type import PatternType
from model.patterns.pattern_constant import PatternCons


class GraAntiPattern(PatternType):
    def __init__(self):
        ident = 'gra-anti-patterns'
        patterns = [
            'FinalDel', 'AccessibilityModify',
            'HiddenApi',
            'ParameterListModifyDep',
            'InheritExtension',
            'ImplementExtension',
            'ReflectUse']
        styles = [
            'del_native_class_final', 'del_native_method_final',
            # 'del_native_class_final_for_var', 'del_native_class_final_for_inherit_and_override',
            'native_class_access_modify', 'native_method_access_modify',
            'call_native_hidden_method', 'use_native_hidden_variable',
            'call_native_hidden_modify_method', 'use_native_hidden_modify_variable',
            'native_method_add_parameter',
            'native_class_inherit_extensive_class',
            'native_class_implement_extensive_interface',
            'extensive_method_reflect_native_method', 'extensive_method_reflect_native_class']
        rules = [
            PatternCons.pattern_final, PatternCons.pattern_access, PatternCons.pattern_hidden,
            PatternCons.pattern_param_modify,
            PatternCons.pattern_inherit_extensive, PatternCons.pattern_implement_extensive,
            PatternCons.pattern_reflect]

        PatternType.__init__(self, ident, patterns, styles, rules)

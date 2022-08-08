import re
from typing import List


class Constant:
    # entity type
    E_method: str = "Method"
    E_variable: str = "Variable"
    E_class: str = "Class"
    E_file: str = "File"
    E_package: str = "Package"
    E_interface: str = "Interface"

    # relation type
    contain: str = "Contain"
    define: str = "Define"
    call: str = "Call"
    param: str = "Parameter"
    use: str = "UseVar"
    implement: str = "Implement"
    inherit: str = "Inherit"
    override: str = 'Override'
    typed: str = 'Typed'
    reflect: str = 'Reflect'

    # anti-pattern name
    ACM: str = "AOSPAccessModify"
    APM: str = "AOSPParameterModify"
    AAM: str = "AOSPAnnotationModify"
    ACAPC: str = "AOSPClassADDParentClass"
    AFD: str = "AOSPFinalDelete"

    # modifier
    accessible_list: List[str] = ['private', 'protected', 'public']
    M_final: str = 'final'
    M_static: str = 'static'
    un_define: str = 'null'

    # rule_type
    sing_rule: int = 0
    multi_rule: int = 1

    # file_name
    file_mc = 'mc\\file-mc.csv'

    # ano
    anonymous_class = 'Anonymous_Class'

    # hidden api sign
    HD_blocked: str = 'blocked'
    HD_unsupported: str = 'unsupported'
    HD_max_target = re.compile('max-target-(.*)')
    HD_sdk: str = 'sdk'
    HD_blacklist: str = 'blacklist'
    HD_greylist: str = 'greylist'
    HD_greylist_max = re.compile('greylist-max-(.*)')
    HD_whitelist: str = 'whitelist'
    HD_greylist_max_label = 'greylist-max-'
    HD_greylist_max_list: List[str] = ['greylist-max-o', 'greylist-max-p']

    @classmethod
    def hidden_map(cls, label: List[str]) -> str:
        if cls.HD_blocked in label or cls.HD_blacklist in label:
            return cls.HD_blacklist
        elif cls.HD_unsupported in label or cls.HD_greylist in label:
            return cls.HD_greylist
        elif cls.HD_sdk in label or cls.HD_whitelist in label:
            return cls.HD_whitelist
        else:
            for max_label in label:
                match = cls.HD_max_target.match(max_label)
                if match:
                    return cls.HD_greylist_max_label + match.group(1)
                match = cls.HD_greylist_max.match(max_label)
                if match:
                    return max_label

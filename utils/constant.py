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

    # hidden api sign
    HD_blocked: str = 'blocked'
    HD_unsupported: str = 'unsupported'
    HD_max_target: List[str] = ['max-target-o', 'max-target-q']

    HD_blacklist: str = 'blacklist'
    HD_greylist: List[str] = ['greylist-max-o', 'greylist-max-q']
    HD_whitelist: str = 'whitelist'

    @classmethod
    def hidden_map(cls, label: List[str]) -> str:
        if cls.HD_blocked in label or cls.HD_unsupported in label or cls.HD_blacklist in label:
            return cls.HD_blacklist
        elif set(label) & set(cls.HD_max_target):
            hd_index = cls.HD_max_target.index(list(set(label) & set(cls.HD_max_target))[0])
            return cls.HD_greylist[hd_index]
        elif set(label) & set(cls.HD_greylist):
            hd_index = cls.HD_max_target.index(list(set(label) & set(cls.HD_greylist))[0])
            return cls.HD_greylist[hd_index]
        else:
            return cls.HD_whitelist

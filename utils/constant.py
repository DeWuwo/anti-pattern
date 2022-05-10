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

    # rule_type
    sing_rule: int = 0
    multi_rule: int = 1

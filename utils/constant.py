class Constant:
    # entity type
    E_method: str = "Method"
    E_variable: str = "Variable"
    E_class: str = "Class"

    # relation type
    contain: str = "contain"
    call: str = "Call"
    para: str = "Para"
    use: str = "Use"
    implement: str = "Implement"
    inherit: str = "Inherit"

    # anti-pattern name
    ACM: str = "AOSPAccessModify"
    APM: str = "AOSPParameterModify"
    AAM: str = "AOSPAnnotationModify"
    ACAPC: str = "AOSPClassADDParentClass"
    AFD: str = "AOSPFinalDelete"

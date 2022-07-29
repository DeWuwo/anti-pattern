import re
from typing import Tuple

MoveRenameMethodFormat = "Move And Rename Method (.*) " \
                         "from class (.*) " \
                         "to (.*) " \
                         "from class (.*)"

MoveMethodFormat = "Move Method (.*) " \
                   "from class (.*) " \
                   "to (.*) " \
                   "from class (.*)"

RenameMethodFormat = "Rename Method (.*) " \
                     "renamed to (.*) " \
                     "in class (.*)"

ExtractMethodFormat = "Extract Method (.*) " \
                      "extracted from (.*) " \
                      "in class (.*)"

ExtractMoveMethodFormat = "Extract And Move Method (.*) " \
                          "extracted from (.*) " \
                          "in class (.*) " \
                          "& moved to class (.*)"

ExtractPattern = Tuple[re.Pattern, int, int, int, int]
EMPattern = re.compile(ExtractMethodFormat)
EMMPattern = re.compile(ExtractMoveMethodFormat)

ExtractMethodPatterns = [(EMMPattern, 2, 3, 1, 4),
                         (EMPattern, 2, 3, 1, 3)]

RenamePattern = Tuple[re.Pattern, int, int, int, int]

MRMPattern = re.compile(MoveRenameMethodFormat)
MMPattern = re.compile(MoveMethodFormat)
RMPattern = re.compile(RenameMethodFormat)

MoveMethodPatterns = [(MRMPattern, 1, 2, 3, 4),
                      (MMPattern, 1, 2, 3, 4),
                      (RMPattern, 3, 1, 2, 3)]

RenameClassFormat = "Rename Class (.*) " \
                    "renamed to (.*)"

MoveClassFormat = "Move Class (.*) " \
                  "moved to (.*)"

MoveRenameClassFormat = "Move And Rename Class (.*) " \
                        "moved and renamed to (.*)"

RCPattern = re.compile(RenameClassFormat)
MRCPattern = re.compile(MoveRenameClassFormat)
MCPattern = re.compile(MoveClassFormat)

MoveClassPatterns = [RCPattern, MRCPattern, MCPattern]

RenameParameterFormat = "Rename Parameter (.*) to (.*) " \
                        "in method (.*) " \
                        "from class (.*)"
RPPattern = re.compile(RenameParameterFormat)

AddParameterFormat = "Add Parameter (.*) " \
                     "in method (.*) " \
                     "from class (.*)"
APPattern = re.compile(RenameParameterFormat)

RemoveParameterFormat = "Remove Parameter (.*) " \
                        "in method (.*) " \
                        "from class (.*)"

RmPPattern = re.compile(RemoveParameterFormat)

MoveAttributeFormat = "Move Attribute " \
                      "(.*) " \
                      "from class (.*) " \
                      "to (.*) " \
                      "from class (.*)"
MAPattern = re.compile(MoveAttributeFormat)

MoveRenameAttributeFormat = "Move And Rename Attribute " \
                            "(.*)" \
                            " renamed to " \
                            "(.*) " \
                            "and moved from class (.*) " \
                            "to class (.*)"
MRAPattern = re.compile(MoveRenameAttributeFormat)

PushUpAttributeFormat = "Pull Up Attribute " \
                        "(.*) " \
                        "from class (.*) " \
                        "to (.*) " \
                        "from class (.*)"

PUAPattern = re.compile(PushUpAttributeFormat)

RenameAttributeFormat = "Rename Attribute (.*) " \
                        "to (.*) " \
                        "in (.*)"
RAPattern = re.compile(RenameAttributeFormat)

MoveAttributePattern = [(MAPattern, 1, 2, 3, 4),
                        (MRAPattern, 1, 2, 3, 4),
                        (PUAPattern, 1, 2, 3, 4),
                        (RAPattern, 1, 2, 3, 3)]
SignatureFormat = "(private|public|package|protected) (.*)(\\(.*\\))"
SignaturePattern = re.compile(SignatureFormat)


def get_rename_method(sig: str) -> str:
    matched = RMPattern.match(sig)
    if matched:
        source_name = matched.group(1)
        print(source_name)
        return source_name
    else:
        assert False


def get_rename_class(sig: str) -> str:
    matched = RCPattern.match(sig)
    if matched:
        source_name = matched.group(1)
        print(source_name)
        return source_name
    else:
        assert False


def get_name_from_sig(sig: str) -> str:
    matched = SignaturePattern.match(sig)
    if matched:
        method_name = matched.group(2)
        return method_name
    else:
        print('get rename error')
        assert False


def get_method_sig_from_code_elements(code_elements):
    for ce in code_elements:
        if ce["codeElementType"] == "METHOD_DECLARATION":
            return ce["codeElement"]
    assert False


def get_rename_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = RPPattern.match(description)
    if matched:
        to_method = matched.group(3)
        to_class = matched.group(4)
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        from_class = to_class
        return from_method, from_class, to_method, to_class
    return None


def get_add_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = APPattern.match(description)
    if matched:
        to_class = matched.group(3)
        to_method = get_method_sig_from_code_elements(refactor_obj["rightSideLocations"])
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        from_class = to_class
        return from_method, from_class, to_method, to_class
    return None


def get_remove_parameter(refactor_obj):
    description = refactor_obj["description"]
    matched = RmPPattern.match(description)
    if matched:
        to_class = matched.group(3)
        from_class = to_class
        from_method = get_method_sig_from_code_elements(refactor_obj["leftSideLocations"])
        to_method = get_method_sig_from_code_elements(refactor_obj["rightSideLocations"])
        return from_method, from_class, to_method, to_class
    return None


SpecialMoveMethodGetters = [get_rename_parameter, get_add_parameter, get_remove_parameter]

ClassNameFormat = "(.*) class (.*)"
ClassNamePattern = re.compile(ClassNameFormat)

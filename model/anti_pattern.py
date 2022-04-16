from model.pattern import Pattern
from model.match import Match
from utils import Constant


class AntiPattern(Pattern):
    anti_patterns = [
        {
            'Android2Honor/InheritClassCouplingDep': [
                [{'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}}, Constant.inherit,
                 {'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}}, '01'],
            ]
        },
        {
            'Android2Honor/ImplementClassCouplingDep': [
                [{'id': [-1], 'category': Constant.E_class, 'attrs': {'accessible': []}}, Constant.implement,
                 {'id': [-1], 'category': Constant.E_interface, 'attrs': {'accessible': []}}, '10'],
            ]
        },
        {
            'Android2Honor/AggregationExtensionInterfaceClassDep': []
        },
        {
            'Android2Honor/ParameterListModifyDep': []
        },
        {
            'Honor2Android/InheritanceUseParentProtected': [
                [{'id': [-1], 'category': 'Class', 'attrs': {'accessible': []}}, 'Inherit',
                 {'id': [-1], 'category': 'Class', 'attrs': {'accessible': []}}, '10'],
                [{'id': ['id', 0, 0], 'category': 'Class', 'attrs': {'accessible': []}}, 'Define',
                 {'id': [-1], 'category': 'Method', 'attrs': {'accessible': []}}, '11'],
                [{'id': ['id', 1, 1], 'category': 'Method', 'attrs': {'accessible': []}}, 'Call',
                 {'id': [-1], 'category': 'Method', 'attrs': {'accessible': ['protected']}}, '10'],
                [{'id': ['id', 0, 1], 'category': 'Class', 'attrs': {'accessible': []}}, 'Define',
                 {'id': ['id', 2, 1], 'category': 'Method', 'attrs': {'accessible': ['protected']}}, '00']
            ]
        },
        {
            'Honor2Android/AggregationAOSPClassDep': []
        },
        {
            'Honor2Android/InnerExtensionClassUseDep': []
        },
        {
            'Honor2Android/EncapsulationAOSPInterface': []
        },
        {
            'Honor2Android/PublicInterfaceUseDep': []
        }
    ]

    def __init__(self, match: Match):
        Pattern.__init__(self, match)

    def start_detect(self):
        print('start detect anti pattern ')
        return self.matchPattern(self.anti_patterns)

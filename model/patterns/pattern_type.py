from typing import List
from model.patterns.pattern_rules import PatternRules


class PatternType:
    ident: str
    patterns: list
    styles: list
    rules: List[PatternRules]

    def __init__(self, ident: str, patterns: list, styles: list, rules: list):
        self.ident = ident
        self.patterns = patterns
        self.styles = styles
        self.rules = rules

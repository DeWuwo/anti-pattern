class PatternType:
    ident: str
    patterns: list
    rules: list

    def __init__(self, ident: str, patterns: list, rules: list):
        self.ident = ident
        self.patterns = patterns
        self.rules = rules

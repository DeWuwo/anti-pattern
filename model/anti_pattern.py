from model.pattern import Pattern
from model.match import Match


class AntiPattern(Pattern):
    anti_patterns = [{'1': []}]

    def __init__(self, match: Match):
        Pattern.__init__(self, match)

    def start_detect(self):
        self.matchPattern(self.anti_patterns)

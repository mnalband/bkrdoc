__author__ = 'Zuzana Baranova'

from bkrdoc.analysis.linter import l_pair_functions, l_single_rules, l_within_phase, l_arg_types


class Linter(object):

    errors = []
    linter_rules = [l_pair_functions.LinterPairFunctions,
                    l_single_rules.LinterSingleRules,
                    l_within_phase.LinterWithinPhase,
                    l_arg_types.LinterArgTypes]

    def __init__(self):
        self.errors = []

    def analyse(self, _list):

        for rule in self.linter_rules:
            rule_ref = rule(_list)
            rule_ref.analyse()
            self.errors += rule_ref.get_errors()


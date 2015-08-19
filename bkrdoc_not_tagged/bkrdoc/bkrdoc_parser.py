#!/usr/bin/python
__author__ = 'Jiri_Kulda'
# description: Simple parser for BeakerLib test

import shlex
import sys
import bkrdoc
import bashlex

class Parser(object):
    """
    Parser is main class. It contains methods for running analysis and nature language information creation.
    Also contains phases containers.
    :param file_in: is path with name to file from which the documentation will be created.
    """
    lexer = shlex

    file_test = ""

    description = ""

    all_commands = ["rlAssert0", "rlAssertEquals", "rlAssertNotEquals",
                    "rlAssertGreater", "rlAssertGreaterOrEqual", "rlAssertExists", "rlAssertNotExists",
                    "rlAssertGrep", "rlAssertNotGrep", "rlAssertDiffer", "rlAssertNotDiffer", "rlRun",
                    "rlWatchdog", "rlReport", "rlIsRHEL", "rlIsFedora", "rlCheckRpm", "rlAssertRpm",
                    "rlAssertNotRpm", "rlAssertBinaryOrigin", "rlGetMakefileRequires",
                    "rlCheckRequirements", "rlCheckMakefileRequires", "rlMount", "rlCheckMount",
                    "rlAssertMount", "rlHash", "rlUnhash", "rlFileBackup", "rlFileRestore",
                    "rlServiceStart", "rlServiceStop", "rlServiceRestore", "rlSEBooleanOn",
                    "rlSEBooleanOff", "rlSEBooleanRestore", "rlCleanupAppend", "rlCleanupPrepend",
                    "rlVirtualXStop", "rlVirtualXGetDisplay", "rlVirtualXStart", "rlWait", "rlWaitForSocket",
                    "rlWaitForFile", "rlWaitForCmd", "rlImport", "rlDejaSum", "rlPerfTime_AvgFromRuns",
                    "rlPerfTime_RunsinTime", "rlLogMetricLow", "rlLogMetricHigh", "rlShowRunningKernel",
                    "rlGetDistroVariant", "rlGetDistroRelease", "rlGetSecondaryArch", "rlGetPrimaryArch",
                    "rlGetArch", "rlShowPackageVersion", "rlFileSubmit", "rlBundleLogs", "rlDie",
                    "rlLogFatal", "rlLogError", "rlLogWarning", "rlLogInfo", "rlLogDebug", "rlLog",
                    "rlGetTestState", "rlGetPhaseState", "rlJournalPrint", "rlJournalPrintText"]

    phases = []
    outside = ""
    file_name = ""

    test_launch = ""

    environmental_variable = []

    def __init__(self, file_in):
        self.phases = []
        self.test_launch = 0
        self.environmental_variable = []
        file_in = file_in.strip()
        if file_in[(len(file_in) - 3):len(file_in)] == ".sh":
            try:
                with open(file_in, "r") as input_file:
                    self.file_name = file_in
                    self.description = file_in[0:(len(file_in) - 3)]
                    self.file_test = input_file.read()
                    self.parse_data()

            except IOError:
                sys.stderr.write("ERROR: Fail to open file: " + file_in + "\n")
                sys.exit(1)

        else:
            print("ERROR: Not a script file. (*.sh)")
            sys.exit(1)

    def parse_data(self):
        """
        Method which divides lines of code into phase containers.
        """
        self.phases.append(bkrdoc.PhaseOutside())
        pom_line = ""
        variables = bkrdoc.TestVariables()
        parsed_file = bashlex.parse(self.file_test)
        data_searcher = bkrdoc.StatementDataSearcher("")
        nodevistor = bkrdoc.NodeVisitor(variables)
        cond = bkrdoc.ConditionsForCommands()

        for command_line in parsed_file:
            nodevistor.visit(command_line)
            data_searcher.parse_command(nodevistor.get_parsed_container())
            nodevistor.erase_parsing_subject_variable()
            argparse_data = data_searcher.parsed_param_ref
            # print argparse_data

            if not cond.is_journal_start(argparse_data.argname) and not cond.is_phase_journal_end(argparse_data.argname):
                if cond.is_phase(argparse_data.argname):
                    p_name = argparse_data.argname[len("rlPhaseStart"):]
                    if argparse_data.description is not None:
                        self.phases.append(bkrdoc.PhaseContainer(p_name + ": " + argparse_data.description))
                    else:
                        self.phases.append(bkrdoc.PhaseContainer(p_name))
                else:
                    self.phases[-1].setup_statement(argparse_data)

            elif cond.is_phase_journal_end(argparse_data.argname) or cond.is_journal_start(argparse_data.argname):
                self.phases.append(bkrdoc.PhaseOutside())

        # print("Started =======================================")
        # self.print_statement()

        # print(variables.variable_names_list)
        # print(variables.variable_values_list)

    def print_statement(self):
        for i in self.phases:
            print(i.phase_name)
            print(i.statement_list)
            print("\n")

    def is_phase_outside(self, phase_ref):
        return phase_ref.phase_name == "Outside phase"

    def is_beakerlib_command(self, testing_command):
        return testing_command in self.all_commands

    def get_phases(self):
        return self.phases

    def get_environmental_variables(self):
        return self.environmental_variable

    def get_file_name(self):
        return self.file_name

    def get_test_launch(self):
        return self.test_launch

    def set_test_launch(self, number_of_variable):
        self.test_launch = number_of_variable
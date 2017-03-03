#!/usr/bin/python
import numpy as np
import csv

from StateMachine import State
from StateMachine import StateMachine
from WalkAction import WalkAction
import constants

# State Machine Pattern (Not sure if best to use this now)
class Waiting(State):
    def run(self):
        print("Waiting for incoming data")
        print self.test


    def next(self, input):
        if input == WalkAction.step_starts:
            return GaitExtractor.stepping

class Stepping(State):
    def run(self):
        print("Currently Stepping")

    def next(self, input):
        if input == WalkAction.step_ends:
            return GaitExtractor.walking


class RTGaitExtractor(StateMachine):
    def __init__(self, logpath=constants.LOG_PATH, state="waiting"):
        # Initial state

        self._startup_procedure_()
        # StateMachine.__init__(self, GaitExtractor.waiting)

    def sample(self, data):
        self.store_raw(data) # Store the raw data if live_stream
        self.evaluate_sample(data)

    # Evaluate Current State and Trigger Actions
    def _evaluate_sample_(self, data):
        if self.current_state == "waiting":
            # do stuff, and trigger an action if required by calling change state with an action
            pass
        elif self.current_state == "stepping":
            # Find end of step and trigger step_end
            pass

    def _store_raw_(self):
        pass

    # Opening new log file, etc
    def _startup_procedure_(self):
        self.current_state = "waiting" # self.current_state = WalkState.Resting
        pass

    # State Processes
    def _stepping_(self):
        # Recording data waiting for step to end
        self.current_state = "stepping"
        # Do Stuff
        print("Step started: waiting for end of step")

    def _processing_(self):
        self.current_state = "processing"
        # Do Stuff
        self.change_state(self, WalkAction.waiting)
        pass

    def _update_display_(self):
        pass


    # State Changer
    def change_state(self, action):
        if action == WalkAction.step_starts:
            self._stepping_()
        elif action == WalkAction.step_ends:
            self._processing_()
            self._update_display_()
        elif action == WalkAction.waiting:
            pass

# GaitExtractor.waiting = Waiting()
# GaitExtractor.stepping = Stepping()


if __name__ == "__main__":
    g = RTGaitExtractor()

    # with open('06_02_17_raw_walk_straight.csv', 'rb') as csvfile:
    #     spanreader = csv.reader(csvfile)
    #     for row in spanreader:


    del g


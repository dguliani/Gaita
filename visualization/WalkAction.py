# StateMachine/mouse/MouseAction.py

class WalkAction:
    def __init__(self, action):
        self.action = action
    def __str__(self): return self.action
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

# Static fields; an enumeration of instances:
WalkAction.waiting = WalkAction("waiting")
WalkAction.step_starts = WalkAction("step starts")
WalkAction.step_ends = WalkAction("step ends")
WalkAction.cleanup = WalkAction("cleanup")
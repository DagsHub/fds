from enum import Enum


# Commands supported by ff
class Commands(Enum):
    INIT = "init"
    STATUS = "status"
    ADD = "add"
    COMMIT = "commit"
    PUSH = "push"
    SAVE = "save"

class AddCommands(Enum):
    ALL = "."

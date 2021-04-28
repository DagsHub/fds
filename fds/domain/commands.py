from enum import Enum


# Commands supported by ff
class Commands(Enum):
    INIT = "init"
    STATUS = "status"
    ADD = "add"
    COMMIT = "commit"

class AddCommands(Enum):
    ALL = "."

from ff.domain.commands import Commands
from ff.logger import Logger


class Run(object):
    def __init__(self, arguments: dict):
        self.logger = Logger.get_logger("ff.Run")
        self.arguments = arguments

    def execute(self):
        arguments = self.arguments
        self.logger.debug(f"arguments passed: {arguments}")
        if arguments["command"] == Commands.INIT:
            # Run init command stuff
            pass
        elif arguments["command"] == Commands.STATUS:
            # Run status command stuff
            pass
        else:
            raise Exception("Invalid operation")

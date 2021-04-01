from ff.domain.commands import Commands
from ff.logger import Logger
from ff.services.dvc_service import DVCService
from ff.services.ff_service import FFService
from ff.services.git_service import GitService


class Run(object):
    def __init__(self, arguments: dict):
        self.logger = Logger.get_logger("ff.Run")
        self.arguments = arguments
        self.service = FFService(GitService(), DVCService())

    def execute(self):
        arguments = self.arguments
        self.logger.debug(f"arguments passed: {arguments}")
        if arguments["command"] == Commands.INIT.value:
            # Run init command stuff
            self.service.init()
            return 0
        elif arguments["command"] == Commands.STATUS.value:
            # Run status command stuff
            self.service.status()
            return 0
        else:
            raise Exception("Invalid operation")

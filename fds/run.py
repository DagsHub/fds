from fds.domain.commands import Commands
from fds.logger import Logger
from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.git_service import GitService


class Run(object):
    def __init__(self, arguments: dict):
        self.logger = Logger.get_logger("fds.Run")
        self.arguments = arguments
        self.service = FdsService(GitService(), DVCService())

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
        elif arguments["command"] == Commands.ADD.value:
            # Run add command stuff
            self.service.add(arguments["add_command"])
            return 0
        elif arguments["command"] == Commands.COMMIT.value:
            # Run commit command stuff
            self.service.commit(arguments["message"])
            return 0
        else:
            raise Exception("Invalid operation")

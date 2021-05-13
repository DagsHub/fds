from shutil import which
import PyInquirer

from fds.domain.commands import Commands
from fds.logger import Logger
from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.git_service import GitService
from fds.services.pretty_print import PrettyPrint
from fds.utils import execute_command


class Run(object):
    def __init__(self, arguments: dict):
        self.logger = Logger.get_logger("fds.Run")
        self.arguments = arguments
        self.service = FdsService(GitService(), DVCService())
        self.printer = PrettyPrint()

    def pre_execute_hook(self):
        # Check if dvc is installed
        if which("dvc") is None:
            self.printer.error("dvc executable is not installed or found")
            questions = [
                {
                    'type': 'confirm',
                    'message': 'Should we install dvc[https://dvc.org/] for you right now?',
                    'name': 'exit',
                    'default': False,
                },
            ]
            answers = PyInquirer.prompt(questions)
            if answers["exit"]:
                execute_command(["pip install dvc"], shell=True, capture_output=False)
            else:
                # Provide instructions
                self.printer.warn("dvc executable is not found, please install dvc from https://dvc.org/doc/install")
            return 0
        if which("git") is None:
            self.printer.error("git executable is not found, please install git from https://git-scm.com/downloads")
            return 0
        pass

    def execute(self):
        # Run pre execute hook
        if self.pre_execute_hook() == 0:
            return 0
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

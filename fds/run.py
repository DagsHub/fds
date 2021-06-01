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
        ret_code = 0
        if which("dvc") is None:
            ret_code = 1
            self.printer.error("dvc executable is not installed or found")
            questions = [
                {
                    'type': 'confirm',
                    'message': 'Should we install dvc [https://dvc.org/] for you right now?\n' +
                               '  Will install using `pip install dvc<3`',
                    'name': 'install',
                    'default': False,
                },
            ]
            answers = PyInquirer.prompt(questions)
            if answers["install"]:
                execute_command(["pip install 'dvc<3'"], shell=True, capture_output=False)
                ret_code = 0
            else:
                # Provide instructions
                self.printer.warn("You can install dvc manually from https://dvc.org/doc/install")

        if which("git") is None:
            self.printer.error("git executable is not found, please install git from https://git-scm.com/downloads")
            ret_code |= 2

        return ret_code

    def execute(self):
        # Run pre execute hook
        hook_ret_code = self.pre_execute_hook()
        if hook_ret_code != 0:
            return hook_ret_code

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
            if len(arguments.get("message", [])) == 1:
                message = arguments["message"][0]
            elif len(arguments.get("m", [])) == 1:
                message = arguments["m"][0]
            else:
                raise Exception("Enter a valid commit message")
            # Run commit command stuff
            self.service.commit(message, arguments['yes'])
            return 0
        else:
            raise Exception("Invalid operation")

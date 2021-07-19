from shutil import which
import PyInquirer
import requests
import sys

from fds.domain.commands import Commands
from fds.logger import Logger
from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.git_service import GitService
from fds.services.pretty_print import PrettyPrint
from fds.utils import execute_command
from .__init__ import __version__


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

        r = requests.get("https://pypi.python.org/pypi/fastds/json")
        data = r.json()
        latest_version = data["info"]["version"]
        if latest_version != __version__:
            questions = [
                {
                    'type': 'confirm',
                    'message': f"You are using fds version {__version__}, however version {latest_version}"
                               f" is available.Should we upgrade using `pip install fastds --upgrade`",
                    'name': 'install',
                    'default': 'True',
                },
            ]
            answers = PyInquirer.prompt(questions)
            if answers["install"]:
                print("\nUpgrading package. Please re-enter the command once upgrade has been completed.\n")
                execute_command(["pip install fastds --upgrade"], shell=True, capture_output=False)
                sys.exit()
            else:
                ret_code = 0

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
        elif arguments["command"] == Commands.CLONE.value:
            # Run clone command stuff
            self.service.clone(arguments["url"], arguments["folder_name"][0], arguments["dvc_remote"])
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
        elif arguments["command"] == Commands.PUSH.value:
            # Run push command stuff
            self.service.push(arguments["git_remote"], arguments["dvc_remote"], arguments["branch"])
            return 0
        elif arguments["command"] == Commands.SAVE.value:
            # Run save command stuff
            self.service.save(arguments["message"], arguments["git_remote"], arguments["dvc_remote"])
            return 0
        else:
            raise Exception("Invalid operation")

import enum
from shutil import which
import PyInquirer
import requests
from pathlib import Path
import sys

from fds.domain.commands import Commands
from fds.logger import Logger
from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.types import InnerService
from fds.services.git_service import GitService
from fds.services.pretty_print import PrettyPrint
from fds.utils import execute_command, rerun_in_new_shell_and_exit
from .__init__ import __version__


class HooksRunner(object):
    class ExitCodes(enum.IntFlag):
        OK = 0
        DVC_INSTALL_FAILED = 2**0
        GIT_INSTALL_FAILED = 2**1
        FDS_UPDATE_FAILED = 2**1
        GIT_INITIALIZE_FAILED = 2**3
        DVC_INITIALIZE_FAILED = 2**4

    def __init__(
        self,
        service: FdsService,
        printer: PrettyPrint,
        logger: Logger,
    ):
        self.service = service
        self.printer = printer
        self.logger = logger

        self.pre_execute_hooks = [
            (self.ExitCodes.DVC_INSTALL_FAILED.value, self._ensure_dvc_installed),
            (self.ExitCodes.GIT_INSTALL_FAILED.value, self._ensure_git_installed),
            (self.ExitCodes.FDS_UPDATE_FAILED.value, self._ensure_fds_updated),
            (self.ExitCodes.GIT_INITIALIZE_FAILED.value, self._ensure_git_initialized),
            (self.ExitCodes.DVC_INITIALIZE_FAILED.value, self._ensure_dvc_initialized),
        ]

    def _ensure_dvc_installed(self):
        if which("dvc") is not None:
            return 0

        ret_code = 1
        self.printer.error("dvc executable is not installed or found")
        questions = [
            {
                'type': 'confirm',
                'message': 'Should we install dvc [https://dvc.org/] for you right now?\n' +
                           '  Will install using `pip3 install dvc<3`',
                'name': 'install',
                'default': False,
            },
        ]
        answers = PyInquirer.prompt(questions)
        if answers["install"]:
            execute_command(["pip3 install 'dvc<3'"], shell=True, capture_output=False)
            ret_code = 0
        else:
            # Provide instructions
            self.printer.warn("You can install dvc manually from https://dvc.org/doc/install")

        return ret_code

    def _ensure_git_installed(self):
        if which("git") is None:
            self.printer.error("git executable is not found, please install git from https://git-scm.com/downloads")
            return sys.exit(-1)
        return 0

    def _ensure_fds_updated(self):
        r = requests.get("https://pypi.python.org/pypi/fastds/json")
        data = r.json()
        latest_version = data["info"]["version"]
        if latest_version == __version__:
            return 0
        questions = [
            {
                'type': 'confirm',
                'message': f"You are using fds version {__version__}, however version {latest_version}"
                           f" is available.Should we upgrade using `pip3 install fastds --upgrade`",
                'name': 'install',
                'default': 'True',
            },
        ]
        answers = PyInquirer.prompt(questions)
        if not answers["install"]:
            return 0

        print("\nUpgrading package.\n")
        execute_command(["pip3 install fastds --upgrade"], shell=True, capture_output=False)
        print("\nfds upgraded. Running command...\n")
        rerun_in_new_shell_and_exit()
        return 0

    def __ensure_initialized(
        self,
        service_name: str,
        service: InnerService,
        raise_on_reject=True,
    ):
        path = Path(service.repo_path).resolve()
        if service.is_initialized():
            return 0

        self.printer.error(f"{service_name} has not been initialized in `{path}`")
        questions = [
            {
                'type': 'confirm',
                'message': f'Should we initialize {service_name} for you right now?\n' +
                           f'  Will initialize in `{path}`',
                'name': 'initialize',
                'default': False,
            },
        ]
        answers = PyInquirer.prompt(questions)
        if answers["initialize"]:
            service.init()
            return 0
        # Provide instructions
        self.printer.warn(
            f"You can initialize {service_name} manually by running `{service_name} init` in `{path}`"
        )
        if raise_on_reject:
            sys.exit(-1)
        return 1

    def _ensure_git_initialized(self):
        return self.__ensure_initialized("git", self.service.git_service)

    def _ensure_dvc_initialized(self):
        return self.__ensure_initialized("dvc", self.service.dvc_service)

    def run(self):
        # Check if dvc is installed
        ret_code = 0
        for exit_code, hook in self.pre_execute_hooks:
            self.logger.debug(f"Running {hook.__qualname__}")
            failed = hook()
            if failed:
                ret_code |= exit_code
        return ret_code


class Run(object):
    def __init__(self, arguments: dict):
        self.logger = Logger.get_logger("fds.Run")
        self.arguments = arguments
        self.service = FdsService(GitService(), DVCService())
        self.printer = PrettyPrint()
        self.hooks_runner = HooksRunner(
            self.service,
            self.printer,
            self.logger,
        )

    def execute(self):
        # Run pre execute hook
        hook_ret_code = self.hooks_runner.run()
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
        elif arguments.get(Commands.VERSION.value):
            self.service.version()
            return 0
        else:
            raise Exception("Invalid operation")

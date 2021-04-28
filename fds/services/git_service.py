import os
from typing import List, Dict, Any

import pygit2

from fds.services.base_service import BaseService
from fds.utils import execute_shell_command


class GitService(BaseService):
    """
    Git Service responsible for all the git commands of fds
    """
    def __init__(self):
        self.repo_path = os.path.curdir

    def init(self) -> bool:
        """
        Responsible for running git init
        :return:
        """
        try:
            pygit2.init_repository(self.repo_path)
            return True
        except:
            return False

    def status(self) -> Any:
        """
        Responsible for running git status
        :return:
        """
        import subprocess
        return subprocess.run(["git", "status"])

    def add(self, add_argument: str) -> Any:
        """
        Responsible for running git add
        :param add_argument: extra agruments of git add
        :return: 
        """
        import subprocess
        return subprocess.run(f"git add {add_argument}", shell=True, capture_output=True)

    def commit(self, message: str) -> Any:
        """
        Responsible for committing into DVC
        :param message: message for dvc
        :return:
        """
        execute_shell_command(f"git commit -m '{message}'")

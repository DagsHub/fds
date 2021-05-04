import os
from typing import Any

import pygit2

from fds.services.base_service import BaseService
from fds.utils import execute_command, convert_bytes_to_string


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
        return execute_command(["git", "status"])

    def add(self, add_argument: str) -> Any:
        """
        Responsible for running git add
        :param add_argument: extra agruments of git add
        :return: 
        """
        git_output = execute_command(["git", "check-ignore", add_argument], capture_output=True)
        if convert_bytes_to_string(git_output.stdout) != '':
            return
        execute_command(["git", "add", add_argument])

    def commit(self, message: str) -> Any:
        """
        Responsible for committing into DVC
        :param message: message for dvc
        :return:
        """
        execute_command(["git", "commit", "-am", message])

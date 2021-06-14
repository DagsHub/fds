import os
from typing import Any

import pygit2

from fds.services.base_service import BaseService
from fds.services.pretty_print import PrettyPrint
from fds.utils import execute_command, convert_bytes_to_string, does_file_exist, check_git_ignore


class GitService(BaseService):
    """
    Git Service responsible for all the git commands of fds
    """
    def __init__(self):
        self.repo_path = os.path.curdir
        self.printer = PrettyPrint()

    def init(self) -> str:
        # Check if git is already initialized
        if does_file_exist(f"{self.repo_path}/.git"):
            return "git already initialized"
        pygit2.init_repository(self.repo_path)
        return "git initialized successfully"

    def status(self) -> Any:
        return execute_command(["git", "status"], capture_output=False)

    def add(self, add_argument: str) -> Any:
        git_output = check_git_ignore(add_argument)
        if convert_bytes_to_string(git_output.stdout) != '':
            return
        # This will take care of adding everything in the argument to add including the .dvc files inside it
        execute_command(["git", "add", add_argument])
        # Explicitly adding the .dvc file in the root because that wont be added by git
        dvc_file = f"{add_argument}.dvc"
        if does_file_exist(dvc_file):
            execute_command(["git", "add", f"{add_argument}.dvc"])
        ignore_file = ".gitignore"
        if does_file_exist(ignore_file):
            execute_command(["git", "add", ignore_file])

    def commit(self, message: str) -> Any:
        execute_command(["git", "commit", "-am", message], capture_output=False)

    @staticmethod
    def push(remote: str, ref: str) -> Any:
        push_cmd = ["git", "push"]
        if remote:
            push_cmd.append(remote)
            if ref:
                push_cmd.append(ref)
            else:
                check_curr_branch = execute_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
                curr_branch = convert_bytes_to_string(check_curr_branch.stdout).rstrip('\n')
                if curr_branch == '':
                    raise Exception("No git branch found to push to")
                push_cmd.append(curr_branch)
        execute_command(push_cmd, capture_output=False)

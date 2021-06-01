import os
from typing import Any, List, Optional
import PyInquirer
from progress.bar import Bar

from fds.domain.commands import AddCommands
from fds.domain.constants import MAX_THRESHOLD_SIZE
from fds.logger import Logger
from fds.services.base_service import BaseService
from fds.services.pretty_print import PrettyPrint
from fds.utils import get_size_of_path, convert_bytes_to_readable, convert_bytes_to_string, execute_command, \
    append_line_to_file, check_git_ignore, check_dvc_ignore, does_file_exist


class DVCService(BaseService):
    """
    DVC Service responsible for all the dvc commands of fds
    """

    def __init__(self):
        self.repo_path = os.path.curdir
        self.logger = Logger.get_logger("fds.DVCService")
        self.printer = PrettyPrint()
        self.selection_message_count = 0

    def init(self):
        """
        Responsible for running dvc init
        :return:
        """
        # Check if dvc is already initialized
        if does_file_exist(f"{self.repo_path}/.dvc"):
            return "DVC already initialized"
        execute_command(["dvc", "init", "--subdir"])
        return "DVC initialized successfully"

    def status(self) -> Any:
        """
        Responsible for running dvc status
        :return:
        """
        return execute_command(["dvc", "status"], capture_output=False)

    def __should_skip_list_add(self, dir: str) -> bool:
        """
        Check if the given dir should be skipped or not
        :param dir: the name of the dir
        :return: True if we should skip, else return False
        """
        if dir == ".":
            return True
        git_output = check_git_ignore(dir)
        if convert_bytes_to_string(git_output.stdout) != '':
            return True
        dvc_output = check_dvc_ignore(dir)
        if convert_bytes_to_string(dvc_output.stdout) != '':
            return True
        return False

    def __skip_already_added(self, root, dirs) -> None:
        # Check if current file is git ignored (this is very similar to adding to dvc also, because as soon as we
        # add to dvc it gets ignored)
        for d in dirs:
            dir = f"{root}/{d}"
            if self.__should_skip_list_add(dir):
                dirs.remove(d)

    def __get_to_add_to_dvc(self, file_or_dir_to_check: str, dirs: List[str], type: str) -> Optional[str]:
        if not self.__should_skip_list_add(file_or_dir_to_check):
            dir_size = get_size_of_path(file_or_dir_to_check)
            if dir_size < MAX_THRESHOLD_SIZE:
                return
            # Show the message only when files are shown and only once per add
            if (self.selection_message_count == 0):
                self.selection_message_count = 1
                self.printer.warn('========== Make your selection, Press "h" for help ==========')
            choices = [{
                "key": "d",
                "name": "Add to DVC",
                "value": "Add to DVC"
            },{
                "key": "g",
                "name": "Add to Git",
                "value": "Add to Git"
            },{
                "key": "i",
                "name": "Ignore - Add to .gitignore",
                "value": "Ignore"
            }]
            if os.path.isdir(file_or_dir_to_check):
                choices.append({
                    "key": "s",
                    "name": "Step Into",
                    "value": "Step Into"
                })

            questions = [
                {
                    "type": "expand",
                    "message": f"What would you like to do with {type} {file_or_dir_to_check} of {convert_bytes_to_readable(dir_size)}?",
                    "name": "selection_choice",
                    "choices": choices,
                    "default": "Add to DVC"
                }
            ]
            answers = PyInquirer.prompt(questions)
            if answers["selection_choice"] == "Add to DVC":
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return file_or_dir_to_check
            elif answers["selection_choice"] == "Add to Git":
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return
            elif answers["selection_choice"] == "Ignore":
                # We should ignore the ./ in beginning when adding to gitignore
                # Add files to gitignore
                append_line_to_file(".gitignore", file_or_dir_to_check[file_or_dir_to_check.startswith('./') and 2:])
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return

    def __add(self, add_argument: str):
        chosen_files_or_folders = []
        # May be add all the folders given in the .gitignore
        folders_to_exclude = ['.git', '.dvc']
        if add_argument == AddCommands.ALL.value:
            path_to_walk = self.repo_path
        else:
            path_to_walk = f"{self.repo_path}/{add_argument}"
        for (root, dirs, files) in os.walk(path_to_walk, topdown=True, followlinks=False):
            # Now skip the un-necessary folders
            [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]
            # Skip the already added files/folders
            self.__skip_already_added(root, dirs)
            # First check root
            folder_to_add = self.__get_to_add_to_dvc(root, dirs, "Dir")
            if folder_to_add is not None:
                chosen_files_or_folders.append(folder_to_add)
            else:
                # Only if they dont select the directory then ask for files, otherwise ignore asking about files of the directory
                # We are also showing if the user chooses to skip becuase the user might not know there is a large file
                # in the directory and choose skip because he dont want the entire directory to be added.
                # Then check files
                for file in files:
                    file_to_add = self.__get_to_add_to_dvc(f"{root}/{file}", [], "File")
                    if file_to_add is not None:
                        chosen_files_or_folders.append(file_to_add)
        self.logger.debug(f"Chosen folders to be added to dvc are {chosen_files_or_folders}")
        if len(chosen_files_or_folders) == 0:
            return "Nothing to add in DVC"

        self.printer.warn("Adding to dvc...")
        progress_tracker = Bar('Processing', max=len(chosen_files_or_folders))
        for add_to_dvc in chosen_files_or_folders:
            execute_command(["dvc", "add", add_to_dvc])
            progress_tracker.next()
        progress_tracker.finish()
        return "DVC add successfully executed"

    def add(self, add_argument: str) -> Any:
        """
        Responsible for adding into dvc
        :return:
        """
        return self.__add(add_argument)

    def commit(self, auto_confirm: bool) -> Any:
        """
        Responsible for committing into DVC
        :param auto_confirm: commit all changed files without confirmation
        :return:
        """
        # In case something is added by user and not committed, we will take care of it
        commit_cmd = ["dvc", "commit", "-q"]
        if auto_confirm:
            commit_cmd.append("-f")
        execute_command(commit_cmd, capture_output=False)

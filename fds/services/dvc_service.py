import os
from enum import Enum
from typing import Any, List, Optional, Tuple
import PyInquirer
from progress.bar import Bar

from fds.domain.commands import AddCommands
from fds.domain.constants import MAX_THRESHOLD_SIZE
from fds.logger import Logger
from fds.services.base_service import BaseService
from fds.services.pretty_print import PrettyPrint
from fds.utils import get_size_of_path, convert_bytes_to_readable, convert_bytes_to_string, execute_command, \
    append_line_to_file, check_git_ignore, check_dvc_ignore, does_file_exist


# Choices for DVC
class DvcChoices(Enum):
    ADD_TO_DVC = "Add to DVC"
    ADD_TO_GIT = "Add to Git"
    IGNORE = "Ignore"
    STEP_INTO = "Step Into"


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

    @staticmethod
    def _get_choice(file_or_dir_to_check: str, path_size: int, type: str) -> dict:
        choices = [{
            "key": "d",
            "name": "Add to DVC",
            "value": DvcChoices.ADD_TO_DVC.value
        },{
            "key": "g",
            "name": "Add to Git",
            "value": DvcChoices.ADD_TO_GIT.value
        },{
            "key": "i",
            "name": "Ignore - Add to .gitignore",
            "value": DvcChoices.IGNORE.value
        }]
        if os.path.isdir(file_or_dir_to_check):
            choices.append({
                "key": "s",
                "name": "Step Into",
                "value": DvcChoices.STEP_INTO.value
            })

        questions = [
            {
                "type": "expand",
                "message": f"What would you like to do with {type} {file_or_dir_to_check} of {convert_bytes_to_readable(path_size)}?",
                "name": "selection_choice",
                "choices": choices,
                "default": DvcChoices.ADD_TO_DVC.value
            }
        ]
        answers = PyInquirer.prompt(questions)
        return answers

    def __get_to_add_to_dvc(self, file_or_dir_to_check: str, dirs: List[str], type: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns the tuple (file/folder to be added to dvc, folder to be ignored)
        :param file_or_dir_to_check: File or folder to check if its to be added or ignored
        :param dirs: folders in the current walk
        :param type: Type indicating whether its file or Dir
        :return: (file/folder to be added to dvc, folder to be ignored)
        """
        if not self.__should_skip_list_add(file_or_dir_to_check):
            path_size = get_size_of_path(file_or_dir_to_check)
            # Dont need to traverse deep in case of dir, if the dir is below the threshold size
            if path_size < MAX_THRESHOLD_SIZE:
                if os.path.isdir(file_or_dir_to_check):
                    return None, file_or_dir_to_check
                return None, None
            # Show the message only when files are shown and only once per add
            if (self.selection_message_count == 0):
                self.selection_message_count = 1
                self.printer.warn('========== Make your selection, Press "h" for help ==========')
            answers = DVCService._get_choice(file_or_dir_to_check=file_or_dir_to_check, path_size=path_size, type=type)
            if answers["selection_choice"] == DvcChoices.ADD_TO_DVC.value:
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return file_or_dir_to_check, None
            elif answers["selection_choice"] == DvcChoices.ADD_TO_GIT.value:
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return None, None
            elif answers["selection_choice"] == DvcChoices.IGNORE.value:
                # We should ignore the ./ in beginning when adding to gitignore
                # Add files to gitignore
                append_line_to_file(".gitignore", file_or_dir_to_check[file_or_dir_to_check.startswith('./') and 2:])
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return None, None
        return None, None

    def __add(self, add_argument: str):
        chosen_files_or_folders = []
        # Keep track of dirs which are below threshold size, so we dont iterate the files inside these dirs
        skipped_dirs = []
        # May be add all the folders given in the .gitignore
        folders_to_exclude = ['.git', '.dvc']
        if add_argument == AddCommands.ALL.value:
            path_to_walk = self.repo_path
        else:
            path_to_walk = f"{self.repo_path}/{add_argument}"
        # if argument is to add a file
        if os.path.isfile(path_to_walk) and get_size_of_path(path_to_walk) >= MAX_THRESHOLD_SIZE:
            # Keep the file in chosen list
            chosen_files_or_folders = [path_to_walk]
        for (root, dirs, files) in os.walk(path_to_walk, topdown=True, followlinks=False):
            # Now skip the un-necessary folders
            [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]
            # Skip the already added files/folders
            self.__skip_already_added(root, dirs)
            # First check root
            (folder_to_add, skipped_dir) = self.__get_to_add_to_dvc(root, dirs, "Dir")
            if skipped_dir is not None:
                skipped_dirs.append(skipped_dir)
            if folder_to_add is not None:
                chosen_files_or_folders.append(folder_to_add)
            else:
                # Only if they dont select the directory then ask for files, otherwise ignore asking about files of the directory
                # We are also showing if the user chooses to skip becuase the user might not know there is a large file
                # in the directory and choose skip because he dont want the entire directory to be added.
                # If the root is skipped because it is below threshold size then we don't need to check files
                if root in skipped_dirs:
                    continue
                # Then check files
                for file in files:
                    (file_to_add, skipped_dir) = self.__get_to_add_to_dvc(f"{root}/{file}", [], "File")
                    if skipped_dir is not None:
                        skipped_dirs.append(skipped_dir)
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

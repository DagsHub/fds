import os
from typing import Any, List, Optional
import PyInquirer

from dvc.api import Repo

from fds.domain.constants import MAX_THRESHOLD_SIZE
from fds.logger import Logger
from fds.services.base_service import BaseService
from fds.utils import get_size_of_path, convert_bytes_to_readable


class DVCService(BaseService):
    """
    DVC Service responsible for all the dvc commands of fds
    """

    def __init__(self):
        self.repo_path = os.path.curdir
        self.logger = Logger.get_logger("fds.DVCService")

    def init(self):
        """
        Responsible for running dvc init
        :return:
        """
        try:
            Repo.init()
            return True
        except:
            return False

    def status(self) -> Any:
        """
        Responsible for running dvc status
        :return:
        """
        import subprocess
        return subprocess.run(["dvc", "status"], capture_output=True)

    def __should_skip_list_add(self, dir: str) -> bool:
        """
        Check if the given dir should be skipped or not
        :param dir: the name of the dir
        :return: True if we should skip, else return False
        """
        if dir == ".":
            return True
        return False

    def __get_to_add_to_dvc(self, file_or_dir_to_check: str, dirs: List[str], type: str) -> Optional[str]:
        if not self.__should_skip_list_add(file_or_dir_to_check):
            dir_size = get_size_of_path(file_or_dir_to_check)
            if dir_size < MAX_THRESHOLD_SIZE:
                return
            questions = [
                {
                    "type": "expand",
                    "message": f"{type} {file_or_dir_to_check} is {convert_bytes_to_readable(dir_size)}",
                    "name": "selection_choice",
                    "choices": [{
                        "key": "y",
                        "name": "Add to DVC",
                        "value": "add"
                    },{
                        "key": "n",
                        "name": "Skip",
                        "value": "skip"
                    },{
                        "key": "s",
                        "name": "Step Into",
                        "value": "step"
                    }],
                    "default": "add"
                }
            ]
            answers = PyInquirer.prompt(questions)
            if answers["selection_choice"] == "add":
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return file_or_dir_to_check
            elif answers["selection_choice"] == "skip":
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return

    def add(self, add_argument: str) -> Any:
        """
        Responsible for adding into dvc
        :return:
        """
        chosen_files_or_folders = []
        # May be add all the folders given in the .gitignore
        folders_to_exclude = ['.git', '.dvc']
        for (root, dirs, files) in os.walk(self.repo_path, topdown=True, followlinks=False):
            # Now skip the un-necessary folders
            [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]
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
        for add_to_dvc in chosen_files_or_folders:
            import subprocess
            subprocess.run(f"dvc add {add_to_dvc} --no-commit", shell=True, capture_output=True)
        return "DVC add successfully executed"

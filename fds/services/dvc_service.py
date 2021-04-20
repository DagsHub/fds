import os
from typing import Any
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

    def add(self, add_argument: str) -> Any:
        """
        Responsible for adding into dvc
        :return:
        """
        chosen_folders_to_add = []
        # May be add all the folders given in the .gitignore
        folders_to_exclude = ['.git', '.dvc']
        for (root, dirs, files) in os.walk(self.repo_path, topdown=True, followlinks=True):
            # We only care about dirs
            dir_to_add = root
            # Now skip the un-necessary folders
            [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]

            if not self.__should_skip_list_add(dir_to_add):
                dir_size = get_size_of_path(dir_to_add)
                if dir_size < MAX_THRESHOLD_SIZE:
                    continue
                questions = [
                    {
                        "type": "expand",
                        "message": f"We have detected that {dir_to_add} is {convert_bytes_to_readable(dir_size)}",
                        "name": "dir_choice",
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
                        "default": True
                    }
                ]
                answers = PyInquirer.prompt(questions)
                if answers["dir_choice"] == "add":
                    chosen_folders_to_add.append(dir_to_add)
                    # Dont need to traverse deep
                    [dirs.remove(d) for d in list(dirs)]
                elif answers["dir_choice"] == "skip":
                    # Dont need to traverse deep
                    [dirs.remove(d) for d in list(dirs)]
        self.logger.debug(f"Chosen folders to be added to dvc are {chosen_folders_to_add}")
        if len(chosen_folders_to_add) == 0:
            return "Nothing to add in DVC"
        for dir_to_add_to_dvc in chosen_folders_to_add:
            import subprocess
            subprocess.run(f"dvc add {dir_to_add_to_dvc} --no-commit", shell=True, capture_output=True)
        return "DVC add successfully executed"

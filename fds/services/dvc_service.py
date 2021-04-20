import os
from typing import Any, Dict

from dvc.api import Repo

from fds.services.base_service import BaseService
from fds.utils import get_size_of_path


class DVCService(BaseService):
    """
    DVC Service responsible for all the dvc commands of fds
    """

    def __init__(self):
        self.repo_path = os.path.curdir

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
        folders_to_exclude = ['.git', '.dvc']
        for (root, dirs, files) in os.walk(self.repo_path, topdown=True, followlinks=True):
            # We only care about dirs
            # Now skip the un-necessary folders
            parent = self.repo_path
            [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]
            print(root)
            dir_to_add = root
            # dir_to_add = f"{parent}/{dir}"
            if not self.__should_skip_list_add(dir_to_add):
                dir_size = get_size_of_path(dir_to_add)
                print(dir_size)


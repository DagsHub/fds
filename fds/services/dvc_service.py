import os
from typing import Any, Dict

from dvc.api import Repo

from fds.services.base_service import BaseService


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

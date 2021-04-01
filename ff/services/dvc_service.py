import os
from dvc.api import Repo

from ff.services.base_service import BaseService


class DVCService(BaseService):
    """
    DVC Service responsible for all the dvc commands of ff
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

    def status(self):
        """
        Responsible for running dvc status
        :return:
        """
        try:
            repo = Repo(self.repo_path)
            repo_status = repo.status()
            if not repo_status:
                return []
            else:
                return repo_status
        except:
            raise Exception("Failed to compute dvc status")

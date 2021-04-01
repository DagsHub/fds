from ff.services.base_service import BaseService
from git import Repo


class GitService(BaseService):
    """
    Git Service responsible for all the git commands of ff
    """
    def init(self):
        """
        Responsible for running git init
        :return:
        """
        Repo.init()

    def status(self):
        """
        Responsible for running git status
        :return:
        """
        print("prints status")

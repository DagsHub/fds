import os
from typing import List

import pygit2
from pygit2 import GIT_STATUS_CURRENT

from fds.services.base_service import BaseService


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

    def status(self) -> List[str]:
        """
        Responsible for running git status
        :return:
        """
        repo = pygit2.Repository(self.repo_path)
        repo_status = repo.status()
        if not repo_status:
            return []
        else:
            return repo_status.keys()

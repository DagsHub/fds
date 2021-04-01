import os
import pygit2

from ff.services.base_service import BaseService
from ff.services.pretty_print import PrettyPrint


class GitService(BaseService):
    """
    Git Service responsible for all the git commands of ff
    """

    def __init__(self):
        self.repo_path = os.path.curdir
        self.printer = PrettyPrint()

    def init(self):
        """
        Responsible for running git init
        :return:
        """
        try:
            pygit2.init_repository(self.repo_path)
            self.printer.success("Git repo initialized successfully")
        except:
            self.printer.error("Git repo failed to initialize")

    def status(self):
        """
        Responsible for running git status
        :return:
        """
        try:
            repo = pygit2.Repository(self.repo_path)
            repo_status = repo.status()
            if not repo_status:
                self.printer.success("Git repo clean")
            else:
                files = "\n".join(repo_status.keys())
                self.printer.warn(f"Dirty files are:\n{files}")
        except:
            self.printer.error("Failed to compute git status")

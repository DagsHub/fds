from fds.services.dvc_service import DVCService
from fds.services.git_service import GitService
from fds.services.pretty_print import PrettyPrint


class FdsService(object):
    """
    Fds Service responsible for all the commands of fds
    """
    # Todo: May be use dependency injection if required
    def __init__(
            self,
            git_service: GitService,
            dvc_service: DVCService
    ):
        self.git_service = git_service
        self.dvc_service = dvc_service
        self.printer = PrettyPrint()

    def init(self):
        """
        fds init
        """
        # Git init
        if self.git_service.init():
            self.printer.success("Git repo initialized successfully")
        else:
            self.printer.error("Git repo failed to initialize")
        # Dvc init
        if self.dvc_service.init():
            self.printer.success("DVC repo initialized successfully")
        else:
            self.printer.error("DVC repo failed to initialize")

    def status(self):
        """
        fds status
        """
        # Git status
        try:
            git_files = self.git_service.status()
            if len(git_files) == 0:
                self.printer.success("Git repo clean")
            else:
                files_to_print = "\n".join(git_files)
                self.printer.warn(f"Untracked git files are:\n{files_to_print}")
        except:
            self.printer.error("Git status failed to execute")
        # Dvc status
        try:
            dvc_files = self.dvc_service.status()
            if len(dvc_files) == 0:
                self.printer.success("DVC repo clean")
            else:
                files_to_print = "\n".join(dvc_files)
                self.printer.warn(f"Untracked dvc files are:\n{files_to_print}")
        except:
            self.printer.error("DVC status failed to execute")

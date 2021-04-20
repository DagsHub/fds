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
            self.printer.success("========== Git repo status ==========")
            status = self.git_service.status()
            self.printer.success(self.printer.convert_bytes_to_str(status.stdout))
            self.printer.error(self.printer.convert_bytes_to_str(status.stderr))
        except:
            self.printer.error("Git status failed to execute")
        # Dvc status
        try:
            self.printer.warn("========== DVC repo status ==========")
            status = self.dvc_service.status()
            self.printer.warn(self.printer.convert_bytes_to_str(status.stdout))
            self.printer.error(self.printer.convert_bytes_to_str(status.stderr))
        except:
            self.printer.error("DVC status failed to execute")

    def add(self, add_command: str):
        """
        fds add
        """
        # First let the user add files into dvc
        # Then remaining goes to git by default
        # Dvc add
        try:
            self.printer.warn("========== DVC add ==========")
            add_msg = self.dvc_service.add(add_command)
            self.printer.success(add_msg)
        except:
            self.printer.error("DVC add failed to execute")

        # Add remaining to git
        try:
            self.git_service.add(add_command)
            self.printer.warn("Git add successfully executed")
        except:
            self.printer.error("Git status failed to execute")

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
        try:
            self.printer.success(self.git_service.init())
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("Git repo failed to initialize")
        # Dvc init
        try:
            self.printer.warn(self.dvc_service.init())
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("DVC repo failed to initialize")

    def status(self):
        """
        fds status
        """
        # Git status
        try:
            self.printer.success("========== Git repo status ==========")
            self.git_service.status()
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("Git status failed to execute")
        # Dvc status
        try:
            self.printer.warn("========== DVC repo status ==========")
            self.dvc_service.status()
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("DVC status failed to execute")

    def add(self, add_command: str):
        """
        fds add
        """
        # First let the user add files into dvc
        # Then remaining goes to git by default
        # Dvc add
        try:
            add_msg = self.dvc_service.add(add_command)
            self.printer.warn(add_msg)
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("DVC add failed to execute")
        # Add remaining to git
        try:
            self.git_service.add(add_command)
            self.printer.success("Git add successfully executed")
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("Git add failed to execute")

    def commit(self, message: str, yes: bool):
        """
        fds commit
        """
        try:
            self.dvc_service.commit(yes)
            self.printer.warn("Successfully committed to DVC")
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("DVC commit failed to execute")
        try:
            self.git_service.commit(message)
            self.printer.success("Successfully committed to Git")
        except Exception as e:
            self.printer.error(str(e))
            raise Exception("Git commit failed to execute")

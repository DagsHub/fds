import sys
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
            sys.exit(1)
        # Dvc init
        if self.dvc_service.init():
            self.printer.success("DVC repo initialized successfully")
        else:
            self.printer.error("DVC repo failed to initialize")
            sys.exit(1)

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
            self.printer.error("Git status failed to execute")
            sys.exit(1)
        # Dvc status
        try:
            self.printer.warn("========== DVC repo status ==========")
            self.dvc_service.status()
        except Exception as e:
            self.printer.error(str(e))
            self.printer.error("DVC status failed to execute")
            sys.exit(1)

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
            self.printer.error("DVC add failed to execute")
            sys.exit(1)
        # Add remaining to git
        try:
            self.git_service.add(add_command)
            self.printer.success("Git add successfully executed")
        except Exception as e:
            self.printer.error(str(e))
            self.printer.error("Git add failed to execute")
            sys.exit(1)

    def commit(self, message: str, yes: bool):
        """
        fds commit
        """
        try:
            self.dvc_service.commit(yes)
            self.printer.warn("Successfully committed to DVC")
        except Exception as e:
            self.printer.error(str(e))
            self.printer.error("DVC commit failed to execute")
            sys.exit(1)
        try:
            self.git_service.commit(message)
            self.printer.success("Successfully committed to Git")
        except Exception as e:
            self.printer.error(str(e))
            self.printer.error("Git commit failed to execute")
            sys.exit(1)

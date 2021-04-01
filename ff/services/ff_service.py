from ff.services.base_service import BaseService
from ff.services.dvc_service import DVCService
from ff.services.git_service import GitService


class FFService(BaseService):
    """
    FF Service responsible for all the commands of ff
    """
    # Todo: May be use dependency injection if required
    def __init__(
            self,
            git_service: GitService,
            dvc_service: DVCService
    ):
        self.git_service = git_service
        self.dvc_service = dvc_service

    def init(self):
        """
        ff init
        """
        # Git init
        self.git_service.init()
        # Dvc init
        self.dvc_service.init()

    def status(self):
        """
        ff status
        """
        # Git status
        self.git_service.status()
        # Dvc status
        self.dvc_service.status()

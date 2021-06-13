from typing import Any


class BaseService(object):
    """
    Base Service responsible for all the commands of fds
    """
    def init(self) -> str:
        """
        The init command
        :return: Success message
        """
        pass

    def status(self) -> Any:
        """
        The status command
        :return: Nothing
        """
        pass

    def add(self, add_argument: str) -> Any:
        """
        The add command
        :return: Nothing
        """
        pass

    def commit(self, message: str) -> Any:
        """
        The commit command
        @param message: Commit message
        :return: Nothing
        """
        pass

    def clone(self, url: str) -> str:
        """
        The clone command
        @param url: The remote url to clone
        :return: The directory name to which the repo is cloned
        """
        pass

    def pull(self, remote: str) -> Any:
        """
        Pulls the repository (latest changes) from remote
        @param remote: The remote name to pull
        :return: Nothing
        """
        pass

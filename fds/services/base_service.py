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

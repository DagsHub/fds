from typing import Any


class BaseService(object):
    """
    Base Service responsible for all the commands of fds
    """
    def init(self) -> bool:
        """
        The init command
        :return: True if init command executes successfully, else False
        """
        pass

    def status(self) -> Any:
        """
        The status command
        :return: Nothing
        """
        pass

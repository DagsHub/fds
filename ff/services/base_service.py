from typing import List


class BaseService(object):
    """
    Base Service responsible for all the commands of ff
    """
    def init(self) -> bool:
        """
        The init command
        :return: True if init command executes successfully, else False
        """
        pass

    def status(self) -> List[str]:
        """
        The status command
        :return: List of untracked changes
        """
        pass

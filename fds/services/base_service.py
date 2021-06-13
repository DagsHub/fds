from typing import Any, Optional


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

    def clone(self, url: str, folder_name: Optional[str]) -> str:
        """
        The clone command
        @param url: The remote url to clone
        @param Optional[folder_name]: Optional folder_name to clone into, if not provided then name from url is used
        :return: The directory name to which the repo is cloned
        """
        pass

    def pull(self, git_url: str, remote: Optional[str]) -> Any:
        """
        Pulls the repository (latest changes) from remote
        @param git_url: git url provided
        @param remote: Optional remote name/url to pull
        :return: Nothing
        """
        pass

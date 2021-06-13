import unittest

from fds.utils import get_git_repo_name_from_url


class TestFds(unittest.TestCase):

    def test_get_git_repo_name_from_url(self):
        repo_name = get_git_repo_name_from_url("git@github.com:DAGsHub/fds.git")
        assert repo_name == "fds"

    def test_get_git_repo_name_from_url_from_https(self):
        repo_name = get_git_repo_name_from_url("https://github.com/DAGsHub/fds.git")
        assert repo_name == "fds"

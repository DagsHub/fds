import unittest

from fds.utils import get_git_repo_name_from_url, construct_dvc_url_from_git_url_dagshub


class TestFds(unittest.TestCase):

    def test_get_git_repo_name_from_url(self):
        repo_name = get_git_repo_name_from_url("git@github.com:DAGsHub/fds.git")
        assert repo_name == "fds"

    def test_get_git_repo_name_from_url_from_https(self):
        repo_name = get_git_repo_name_from_url("https://github.com/DAGsHub/fds.git")
        assert repo_name == "fds"

    def test_get_git_repo_name_from_url_without_suffix(self):
        repo_name = get_git_repo_name_from_url("https://github.com/DAGsHub/fds")
        assert repo_name == "fds"

    def test_construct_dvc_url_from_git_url_dagshub(self):
        repo_url = construct_dvc_url_from_git_url_dagshub("https://github.com/DAGsHub/fds.git")
        assert repo_url == "https://github.com/DAGsHub/fds.dvc"

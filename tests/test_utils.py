import unittest

from validators import ValidationFailure

from fds.utils import get_git_repo_name_from_url, construct_dvc_url_from_git_url_dagshub, is_url


class TestFds(unittest.TestCase):

    def test_get_git_repo_name_from_url(self):
        repo_name = get_git_repo_name_from_url("git@github.com:DAGsHub/fds.git")
        assert repo_name == "fds"

    def test_get_git_repo_name_from_url_from_https(self):
        repo_name = get_git_repo_name_from_url("https://github.com/DAGsHub/fds.git")
        assert repo_name == "fds"

    def test_construct_dvc_url_from_git_url_dagshub(self):
        repo_url = construct_dvc_url_from_git_url_dagshub("https://github.com/DAGsHub/fds.git")
        assert repo_url == "https://github.com/DAGsHub/fds.dvc"

    def test_is_url(self):
        isUrl = is_url("https://github.com/DAGsHub/fds.git")
        assert isUrl == True

    def test_is_not_url(self):
        isUrl = is_url("foobar")
        assert type(isUrl) == ValidationFailure

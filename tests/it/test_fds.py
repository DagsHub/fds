import os

from fds.utils import does_file_exist, execute_command
from tests.it.helpers import IntegrationTestCase


class TestFds(IntegrationTestCase):

    def test_init_success(self):
        os.chdir(self.repo_path)
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git")
        assert does_file_exist(f"{self.repo_path}/.dvc")

    def test_init_git_exists(self):
        os.chdir(self.repo_path)
        execute_command(["git", "init"])
        assert does_file_exist(f"{self.repo_path}/.git") is True
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git") is True
        assert does_file_exist(f"{self.repo_path}/.dvc") is True

    def test_init_dvc_exists(self):
        os.chdir(self.repo_path)
        execute_command(["dvc", "init", "--no-scm"])
        assert does_file_exist(f"{self.repo_path}/.dvc") is True
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git") is True
        assert does_file_exist(f"{self.repo_path}/.dvc") is True


from fds.utils import does_file_exist, execute_command
from tests.it.helpers import IntegrationTestCase


class TestGit(IntegrationTestCase):

    def test_init_git(self):
        self.git_service.init()
        assert does_file_exist(f"{self.repo_path}/.git") is True

    def test_init_git_already_exists(self):
        execute_command(["git", "init"])
        assert does_file_exist(f"{self.repo_path}/.git") is True
        msg = self.git_service.init()
        assert msg == "git already initialized"

    def test_status(self):
        self.git_service.status()

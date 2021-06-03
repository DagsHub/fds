from fds.utils import does_file_exist, execute_command
from tests.it.helpers import IntegrationTestCase


class TestFds(IntegrationTestCase):

    def test_init_success(self):
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git")
        assert does_file_exist(f"{self.repo_path}/.dvc")

    def test_double_init(self):
        self.fds_service.init()
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git") is True
        assert does_file_exist(f"{self.repo_path}/.dvc") is True

    def test_status(self):
        self.fds_service.status()

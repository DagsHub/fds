from fds.utils import does_file_exist, execute_command
from tests.it.helpers import IntegrationTestCase


class TestFds(IntegrationTestCase):

    def test_init_success(self):
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git")
        assert does_file_exist(f"{self.repo_path}/.dvc")

    def test_status(self):
        self.fds_service.status()

    def test_add(self):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add("large_file")

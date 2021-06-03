from fds.utils import does_file_exist, execute_command
from tests.it.helpers import IntegrationTestCase

class TestDvc(IntegrationTestCase):

    def test_init_dvc(self):
        self.git_service.init()
        self.dvc_service.init()
        assert does_file_exist(f"{self.repo_path}/.dvc") is True

    def test_init_git_already_exists(self):
        execute_command(["dvc", "init", "--no-scm"])
        assert does_file_exist(f"{self.repo_path}/.dvc") is True
        msg = self.dvc_service.init()
        assert msg == "DVC already initialized"
        assert does_file_exist(f"{self.repo_path}/.dvc") is True

    def test_init_dvc_failure(self):
        # Without git, dvc initialization fails without --no-scm
        self.assertRaises(Exception, self.dvc_service.init)

    def test_status(self):
        self.dvc_service.status()

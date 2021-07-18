from unittest.mock import patch

from fds.services.dvc_service import DvcChoices
from fds.utils import does_file_exist, execute_command, convert_bytes_to_string
from tests.it.helpers import IntegrationTestCase


class TestFds(IntegrationTestCase):

    def test_init_success(self):
        self.fds_service.init()
        assert does_file_exist(f"{self.repo_path}/.git")
        assert does_file_exist(f"{self.repo_path}/.dvc")

    def test_status(self):
        self.fds_service.init()
        self.fds_service.status()

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_add(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add(["."])
        output = execute_command(["git", "status"], capture_output=True)
        # Check DVC add
        assert "new file:   large_file.dvc" in convert_bytes_to_string(output.stdout)
        # Check Git add
        assert "new file:   git_data/file-0" in convert_bytes_to_string(output.stdout)
        assert "new file:   git_data/file-1" in convert_bytes_to_string(output.stdout)
        assert "new file:   git_data/file-2" in convert_bytes_to_string(output.stdout)
        assert "new file:   git_data/file-3" in convert_bytes_to_string(output.stdout)
        assert "new file:   git_data/file-4" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_add_multiple_paths(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_dummy_file("large_file_1", 11 * 1024)
        super().create_dummy_file("large_file_2", 11 * 1024)
        super().create_dummy_file("large_file_3", 11 * 1024)
        self.fds_service.add(["large_file_1", "large_file_3"])
        output = execute_command(["git", "status"], capture_output=True)
        # Check DVC add
        assert "new file:   large_file_3.dvc" in convert_bytes_to_string(output.stdout)
        assert "new file:   large_file_1.dvc" in convert_bytes_to_string(output.stdout)
        assert "\n\tlarge_file_2" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.IGNORE.value})
    def test_add_dvc_ignore(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add(["."])
        output = execute_command(["cat", ".dvcignore"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_commit(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add(["."])
        self.fds_service.commit("Commit 1", True)
        output = execute_command(["git", "log", "--oneline"], capture_output=True)
        assert "Commit 1" in convert_bytes_to_string(output.stdout)
        output = execute_command(["dvc", "dag"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)
        super().create_fake_dvc_data()
        self.fds_service.commit("Commit 2", True)
        output = execute_command(["git", "log", "--oneline"], capture_output=True)
        assert "Commit 2" in convert_bytes_to_string(output.stdout)
        output = execute_command(["git", "diff", "--raw", "HEAD~1"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.SKIP.value})
    def test_skip_in_add(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add(["."])
        output = execute_command(["git", "status"], capture_output=True)
        # This means untracked, because added files will have new file: in git output
        assert "\n\tlarge_file\n\n" in convert_bytes_to_string(output.stdout)

    def test_commit_git(self):
        self.fds_service.init()
        super().create_fake_git_data()
        self.fds_service.add(["."])
        self.fds_service.commit("Commit 1", False)
        output = execute_command(["git", "log", "--oneline"], capture_output=True)
        assert "Commit 1" in convert_bytes_to_string(output.stdout)

    def test_clone(self):
        self.fds_service.clone(self.get_remote_url_for_test(), None, None)
        # Check git clone
        assert does_file_exist(f"{self.repo_path}/hello-world")
        # Checking dvc pull
        assert does_file_exist(f"{self.repo_path}/hello-world/data")

    def test_clone_empty(self):
        self.fds_service.clone(self.get_remote_url_for_test(), "", None)
        # Check git clone
        assert does_file_exist(f"{self.repo_path}/hello-world")
        # Checking dvc pull
        assert does_file_exist(f"{self.repo_path}/hello-world/data")

    def test_clone_git_custom_name(self):
        self.fds_service.clone(self.get_remote_url_for_test(), "test", None)
        # Check git clone
        assert does_file_exist(f"{self.repo_path}/test")
        # Checking dvc pull
        assert does_file_exist(f"{self.repo_path}/test/data")

    def test_clone_given_remote(self):
        url = "https://github.com/iterative/example-get-started.git"
        self.fds_service.clone(url, "start", "storage")
        # Check git clone
        assert does_file_exist(f"{self.repo_path}/start")
        # Checking dvc pull of storage remote
        assert does_file_exist(f"{self.repo_path}/start/data/data.xml")

import os
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
        self.fds_service.add(".")
        output = execute_command(["git", "status"], capture_output=True)
        # Check DVC add
        assert f"new file:   large_file.dvc" in convert_bytes_to_string(output.stdout)
        # Check Git add
        assert f"new file:   git_data/file-0" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-1" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-2" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-3" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-4" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_commit(self, get_choice):
        self.fds_service.init()
        super().create_fake_git_data()
        super().create_fake_dvc_data()
        self.fds_service.add(".")
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

    def test_commit_git(self):
        self.fds_service.init()
        super().create_fake_git_data()
        self.fds_service.add(".")
        self.fds_service.commit("Commit 1", False)
        output = execute_command(["git", "log", "--oneline"], capture_output=True)
        assert "Commit 1" in convert_bytes_to_string(output.stdout)


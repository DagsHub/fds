import os
from unittest.mock import patch

from fds.services.dvc_service import DvcChoices
from fds.utils import does_file_exist, execute_command, convert_bytes_to_string
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

    def test_add(self):
        self.git_service.init()
        self.dvc_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file" in convert_bytes_to_string(output.stdout)
        msg = self.dvc_service.add("large_file")
        assert does_file_exist(f"{self.repo_path}/large_file.dvc")
        assert msg == "DVC add successfully executed"

    def test_add_nothing(self):
        self.git_service.init()
        self.dvc_service.init()
        super().create_fake_dvc_data()
        msg = self.dvc_service.add(f"dvc_data/file-0")
        assert msg == "Nothing to add in DVC"

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.IGNORE.value})
    def test_add_check_ignore(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file" in convert_bytes_to_string(output.stdout)
        assert does_file_exist(f".gitignore") is False
        msg = self.dvc_service.add(".")
        assert does_file_exist(f".gitignore") is True
        assert msg == "Nothing to add in DVC"
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file" not in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_GIT.value})
    def test_add_check_add_git(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file" in convert_bytes_to_string(output.stdout)
        msg = self.dvc_service.add(".")
        assert msg == "Nothing to add in DVC"

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_add_check_add_dvc(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file" in convert_bytes_to_string(output.stdout)
        msg = self.dvc_service.add(".")
        assert msg == "DVC add successfully executed"
        output = execute_command(["git", "status"], capture_output=True)
        assert f"large_file.dvc" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_commit_auto_confirm(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        self.dvc_service.add(".")
        self.dvc_service.commit(True)
        execute_command(["git", "add", "large_file.dvc"], capture_output=True)
        output = execute_command(["dvc", "dag"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)
        super().create_fake_dvc_data()
        self.dvc_service.commit(True)
        output = execute_command(["git", "diff", "--raw"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_commit_no_auto_confirm(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        self.dvc_service.add(".")
        self.dvc_service.commit(False)
        output = execute_command(["dvc", "dag"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)

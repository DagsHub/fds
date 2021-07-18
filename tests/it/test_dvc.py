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
        assert "large_file" in convert_bytes_to_string(output.stdout)
        dvc_add = self.dvc_service.add(["large_file"])
        assert does_file_exist(f"{self.repo_path}/large_file.dvc")
        assert dvc_add.files_added_to_dvc[0] == "./large_file"

    def test_add_multiple(self):
        self.git_service.init()
        self.dvc_service.init()
        super().create_fake_git_data()
        super().create_dummy_file("large_file_1", 11 * 1024)
        super().create_dummy_file("large_file_2", 11 * 1024)
        super().create_dummy_file("large_file_3", 11 * 1024)
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file_1" in convert_bytes_to_string(output.stdout)
        assert "large_file_2" in convert_bytes_to_string(output.stdout)
        assert "large_file_3" in convert_bytes_to_string(output.stdout)
        dvc_add = self.dvc_service.add(["large_file_1", "large_file_3"])
        assert does_file_exist(f"{self.repo_path}/large_file_1.dvc")
        assert does_file_exist(f"{self.repo_path}/large_file_3.dvc")
        assert "./large_file_1" in dvc_add.files_added_to_dvc
        assert "./large_file_3" in dvc_add.files_added_to_dvc

    def test_add_nothing(self):
        self.git_service.init()
        self.dvc_service.init()
        super().create_fake_dvc_data()
        dvc_add = self.dvc_service.add(["dvc_data/file-0"])
        assert len(dvc_add.files_added_to_dvc) == 0

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.IGNORE.value})
    def test_add_check_ignore(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)
        assert does_file_exist(".gitignore") is False
        dvc_add = self.dvc_service.add(["."])
        assert does_file_exist(".gitignore") is True
        assert len(dvc_add.files_added_to_dvc) == 0
        output = execute_command(["cat", ".dvcignore"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file" not in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_GIT.value})
    def test_add_check_add_git(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)
        dvc_add = self.dvc_service.add(["."])
        assert len(dvc_add.files_added_to_dvc) == 0

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_add_check_add_dvc(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)
        dvc_add = self.dvc_service.add(["."])
        assert dvc_add.files_added_to_dvc[0] == "./large_file"
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.SKIP.value})
    def test_skip_check_add_dvc(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        output = execute_command(["git", "status"], capture_output=True)
        assert "large_file" in convert_bytes_to_string(output.stdout)
        dvc_add = self.dvc_service.add(["."])
        assert len(dvc_add.files_added_to_dvc) == 0
        assert dvc_add.files_skipped[0] == "./large_file"

    @patch("fds.services.dvc_service.DVCService._get_choice", return_value={"selection_choice": DvcChoices.ADD_TO_DVC.value})
    def test_commit_auto_confirm(self, get_choice):
        self.fds_service.init()
        super().create_fake_dvc_data()
        self.dvc_service.add(["."])
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
        self.dvc_service.add(["."])
        self.dvc_service.commit(False)
        output = execute_command(["dvc", "dag"], capture_output=True)
        assert "large_file.dvc" in convert_bytes_to_string(output.stdout)

    def test_clone(self):
        self.fds_service.clone(self.get_remote_url_for_test(), None, None)
        assert does_file_exist(f"{self.repo_path}/hello-world")
        # Checking dvc pull
        assert does_file_exist(f"{self.repo_path}/hello-world/data")

    def test_clone_with_remote_name(self):
        folder_name = self.git_service.clone(self.get_remote_url_for_test(), None)
        os.chdir(folder_name)
        self.dvc_service.pull(self.get_remote_url_for_test(), "origin")
        assert does_file_exist(f"{self.repo_path}/hello-world/data")

    def test_clone_dagshub_url(self):
        folder_name = self.git_service.clone(self.get_remote_url_for_test(), None)
        os.chdir(folder_name)
        self.dvc_service.pull(self.get_remote_url_for_test(), None)
        assert does_file_exist(f"{self.repo_path}/hello-world/data")

    @patch("fds.services.dvc_service.DVCService._show_choice_of_remotes", return_value="storage")
    def test_clone_show_remotes_list(self, get_choice):
        url = "https://github.com/iterative/example-get-started.git"
        folder_name = self.git_service.clone(url, None)
        os.chdir(folder_name)
        self.dvc_service.pull(url, None)
        assert does_file_exist(f"{self.repo_path}/example-get-started/data/data.xml")

    @patch("fds.services.dvc_service.DVCService._show_choice_of_remotes", return_value="storage")
    def test_clone_given_remote(self, get_choice):
        url = "https://github.com/iterative/example-get-started.git"
        folder_name = self.git_service.clone(url, None)
        os.chdir(folder_name)
        self.dvc_service.pull(url, "storage")
        assert does_file_exist(f"{self.repo_path}/example-get-started/data/data.xml")

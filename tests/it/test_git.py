from fds.utils import does_file_exist, execute_command, convert_bytes_to_string
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

    def test_add(self):
        self.git_service.init()
        super().create_fake_git_data()
        self.git_service.add(".")
        output = execute_command(["git", "status"], capture_output=True)
        assert convert_bytes_to_string(output.stderr) == ""
        assert f"new file:   git_data/file-0" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-1" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-2" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-3" in convert_bytes_to_string(output.stdout)
        assert f"new file:   git_data/file-4" in convert_bytes_to_string(output.stdout)

    def test_add_one(self):
        self.git_service.init()
        super().create_fake_git_data()
        self.git_service.add("git_data/file-0")
        output = execute_command(["git", "status"], capture_output=True)
        assert convert_bytes_to_string(output.stderr) == ""
        assert f"new file:   git_data/file-0" in convert_bytes_to_string(output.stdout)
        assert "Untracked files:" in convert_bytes_to_string(output.stdout)
        assert "file-1" in convert_bytes_to_string(output.stdout)
        assert "file-2" in convert_bytes_to_string(output.stdout)
        assert "file-3" in convert_bytes_to_string(output.stdout)
        assert "file-4" in convert_bytes_to_string(output.stdout)

    def test_add_gitignore(self):
        self.git_service.init()
        super().create_fake_git_data()
        super().create_dummy_file(".gitignore", 100)
        self.git_service.add("git_data/file-0")
        output = execute_command(["git", "status"], capture_output=True)
        assert f"new file:   git_data/file-0" in convert_bytes_to_string(output.stdout)
        assert f"new file:   .gitignore" in convert_bytes_to_string(output.stdout)

    def test_commit(self):
        self.git_service.init()
        super().create_fake_git_data()
        self.git_service.add(".")
        self.git_service.commit("Commit 1")
        output = execute_command(["git", "log", "--oneline"], capture_output=True)
        assert "Commit 1" in convert_bytes_to_string(output.stdout)


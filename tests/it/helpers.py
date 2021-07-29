import os
import shutil
import unittest
import tempfile
from pathlib import Path

from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.git_service import GitService


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.repo_path = tempfile.mkdtemp()
        self.git_service = GitService()
        self.dvc_service = DVCService()
        self.fds_service = FdsService(self.git_service, self.dvc_service)
        os.chdir(self.repo_path)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.repo_path)

    def create_fake_git_data(self):
        git_path = f"{self.repo_path}/git_data"
        Path(git_path).mkdir(parents=True, exist_ok=True)
        # Creating 5 random files
        for i in range(0, 5):
            self.create_dummy_file(f"{git_path}/file-{i}", 10)

    def create_dummy_file(self, file_name: str, size: int):
        with open(file_name, 'wb') as fout:
            fout.write(os.urandom(size))

    def create_fake_dvc_data(self):
        dvc_path = f"{self.repo_path}/dvc_data"
        Path(dvc_path).mkdir(parents=True, exist_ok=True)
        # creating a big folder
        for i in range(0, 101):
            self.create_dummy_file(f"{dvc_path}/file-{i}", 10)
        # creating one large file
        self.create_dummy_file("large_file", 11 * 1024)

    def get_remote_url_for_test(self):
        return "https://dagshub.com/mohithg/hello-world.git"

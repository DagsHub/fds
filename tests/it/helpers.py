import os
import shutil
import unittest
import tempfile

from fds.services.dvc_service import DVCService
from fds.services.fds_service import FdsService
from fds.services.git_service import GitService


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.repo_path = tempfile.mkdtemp()
        self.git_service = GitService(self.repo_path)
        self.dvc_service = DVCService(self.repo_path)
        self.fds_service = FdsService(self.git_service, self.dvc_service)
        os.chdir(self.repo_path)

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.repo_path)

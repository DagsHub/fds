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
        self.fds_service = FdsService(GitService(self.repo_path), DVCService(self.repo_path))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.repo_path)

import unittest
from unittest.mock import patch

from fds.services.fds_service import FdsService


class TestFds(unittest.TestCase):

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_init_success(self, mock_git_service, mock_dvc_service):
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.init()
        assert mock_git_service.init.called
        assert mock_dvc_service.init.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_status_success(self, mock_git_service, mock_dvc_service):
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.status()
        assert mock_git_service.status.called
        assert mock_dvc_service.status.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_status_git_failure(self, mock_git_service, mock_dvc_service):
        mock_git_service.status.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.status()
        self.assertRaises(Exception, mock_git_service.status)
        assert mock_git_service.status.called
        assert mock_dvc_service.status.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_status_dvc_failure(self, mock_git_service, mock_dvc_service):
        mock_dvc_service.status.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.status()
        self.assertRaises(Exception, mock_dvc_service.status)
        assert mock_git_service.status.called
        assert mock_dvc_service.status.called

import unittest
from unittest.mock import patch
import pytest
import re

from fds import __version__
from fds.services.fds_service import FdsService
from fds.run import HooksRunner

BOOLS = [True, False]


#  NOTE unittest.mock:_Call backport
def patch_unittest_mock_call_cls():
    import sys
    if sys.version_info.minor >= 8:
        return

    import unittest.mock

    def _get_call_arguments(self):
        if len(self) == 2:
            args, kwargs = self
        else:
            name, args, kwargs = self

        return args, kwargs

    @property
    def args(self):
        return self._get_call_arguments()[0]

    @property
    def kwargs(self):
        return self._get_call_arguments()[1]

    unittest.mock._Call._get_call_arguments = _get_call_arguments
    unittest.mock._Call.args = args
    unittest.mock._Call.kwargs = kwargs


patch_unittest_mock_call_cls()


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
        self.assertRaises(Exception, mock_git_service.status)
        self.assertRaises(Exception, fds_service.status)
        assert mock_git_service.status.called
        assert mock_dvc_service.status.notcalled

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_status_dvc_failure(self, mock_git_service, mock_dvc_service):
        mock_dvc_service.status.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        self.assertRaises(Exception, fds_service.status)
        self.assertRaises(Exception, mock_dvc_service.status)
        assert mock_git_service.status.called
        assert mock_dvc_service.status.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_add_success(self, mock_git_service, mock_dvc_service):
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.add(".")
        assert mock_git_service.add.called
        assert mock_dvc_service.add.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_add_git_failure(self, mock_git_service, mock_dvc_service):
        mock_git_service.add.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        self.assertRaises(Exception, mock_git_service.add)
        with self.assertRaises(Exception):
            fds_service.add(".")
        assert mock_git_service.add.called
        assert mock_dvc_service.add.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_add_dvc_failure(self, mock_git_service, mock_dvc_service):
        mock_dvc_service.add.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        with self.assertRaises(Exception):
            fds_service.add(".")
        self.assertRaises(Exception, mock_dvc_service.add)
        assert mock_dvc_service.add.called
        assert mock_git_service.add.notcalled

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_commit_success(self, mock_git_service, mock_dvc_service):
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        fds_service.commit("some commit message", True)
        assert mock_git_service.commit.called
        assert mock_dvc_service.commit.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_commit_git_failure(self, mock_git_service, mock_dvc_service):
        mock_git_service.commit.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        with self.assertRaises(Exception):
            fds_service.commit("some commit message", True)
        self.assertRaises(Exception, mock_git_service.commit)
        assert mock_git_service.commit.called
        assert mock_dvc_service.commit.called

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_commit_dvc_failure(self, mock_git_service, mock_dvc_service):
        mock_dvc_service.commit.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        with self.assertRaises(Exception):
            fds_service.commit("some commit message", False)
        self.assertRaises(Exception, mock_dvc_service.commit)
        assert mock_dvc_service.commit.called
        assert mock_git_service.commit.notcalled

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_clone_dvc_failure(self, mock_git_service, mock_dvc_service):
        mock_dvc_service.pull.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        with self.assertRaises(Exception):
            fds_service.clone("https://github.com/dagshub/fds.git", None, None)
        self.assertRaises(Exception, mock_dvc_service.pull)
        mock_git_service.clone.assert_called_with("https://github.com/dagshub/fds.git", None)

    @patch('fds.services.dvc_service.DVCService')
    @patch('fds.services.git_service.GitService')
    def test_clone_git_failure(self, mock_git_service, mock_dvc_service):
        mock_git_service.clone.side_effect = Exception
        fds_service = FdsService(mock_git_service, mock_dvc_service)
        with self.assertRaises(Exception):
            fds_service.clone("https://github.com/dagshub/fds.git", None, None)
        self.assertRaises(Exception, mock_git_service.clone)
        assert mock_dvc_service.pull.notcalled


class TestFdsHooks:

    @pytest.mark.parametrize("dvc_preinstalled", BOOLS)
    @pytest.mark.parametrize("install_prompt_accept", BOOLS)
    @patch('fds.run.execute_command')
    @patch('fds.run.PyInquirer.prompt')
    @patch('fds.services.fds_service.FdsService')
    @patch('fds.run.which')
    def test_dvc_installed(
        self,
        mock_which,
        mock_fds_service,
        mock_prompt,
        mock_execute_command,
        dvc_preinstalled: bool,
        install_prompt_accept: bool
    ):
        mock_which.return_value = dvc_preinstalled or None
        mock_prompt.return_value = {"install": install_prompt_accept}
        hooks_runner = HooksRunner(
            mock_fds_service.service,
            mock_fds_service.printer,
            mock_fds_service.logger,
        )
        ret = hooks_runner._ensure_dvc_installed()
        mock_which.assert_called_with("dvc")
        if dvc_preinstalled:
            return

        assert mock_prompt.call_count == 1

        if not install_prompt_accept:
            assert ret != 0
            # TODO validate printer containing "install dvc manually"
            return
        assert ret == 0
        assert mock_execute_command.call_count == 1

        args = mock_execute_command.call_args_list[0].args[0]
        assert re.findall(r"^pip install .*'dvc", args[0])

    @pytest.mark.parametrize("git_preinstalled", BOOLS)
    @patch('fds.run.sys.exit')
    @patch('fds.services.fds_service.FdsService')
    @patch('fds.run.which')
    def test_git_installed(
        self,
        mock_which,
        mock_fds_service,
        mock_sys_exit,
        git_preinstalled: bool,
    ):
        mock_which.return_value = git_preinstalled or None
        hooks_runner = HooksRunner(
            mock_fds_service.service,
            mock_fds_service.printer,
            mock_fds_service.logger,
        )
        ret = hooks_runner._ensure_git_installed()
        mock_which.assert_called_with("git")
        if git_preinstalled:
            assert ret == 0
            return

        assert mock_sys_exit.call_count == 1
        assert 0 not in mock_sys_exit.called_with

    @pytest.mark.parametrize("is_latest", BOOLS)
    @pytest.mark.parametrize("install_prompt_accept", BOOLS)
    @patch('fds.run.rerun_in_new_shell_and_exit')
    @patch('fds.run.execute_command')
    @patch('fds.run.PyInquirer.prompt')
    @patch('fds.services.fds_service.FdsService')
    @patch('fds.run.requests.get')
    def test_fds_update(
        self,
        mock_requests_get,
        mock_fds_service,
        mock_prompt,
        mock_execute_command,
        mock_rerun,
        is_latest: bool,
        install_prompt_accept: bool
    ):
        mock_requests_get.return_value = type(
            "Response",
            (),
            {
                "json": lambda self: {
                    "info": {
                        "version": __version__ + ("b3" if not is_latest else "")
                    }
                }
            }
        )()
        mock_prompt.return_value = {"install": install_prompt_accept}

        hooks_runner = HooksRunner(
            mock_fds_service.service,
            mock_fds_service.printer,
            mock_fds_service.logger,
        )
        ret = hooks_runner._ensure_fds_updated()
        mock_requests_get.assert_called_with("https://pypi.python.org/pypi/fastds/json")
        assert ret == 0
        if is_latest:
            return
        assert mock_prompt.call_count == 1
        # # TODO validate stdout contains "Should we upgrade..."
        if not install_prompt_accept:
            return

        assert mock_execute_command.call_count == 1

        lst = mock_execute_command.call_args_list[0]
        assert re.findall(r"^pip install .*fastds.*--upgrade", lst.args[0][0])

        assert mock_rerun.call_count == 1
        mock_rerun.assert_called_with()

    @pytest.mark.parametrize("raise_on_reject", BOOLS)
    @pytest.mark.parametrize("service_preinitialized", BOOLS)
    @pytest.mark.parametrize("initialize_prompt_accept", BOOLS)
    @pytest.mark.parametrize("service_name", ["git", "dvc"])
    @patch('fds.run.sys.exit')
    @patch('fds.run.PyInquirer.prompt')
    @patch('fds.services.fds_service.FdsService')
    def test_service_initialized(
        self,
        mock_fds_service,
        mock_prompt,
        mock_sys_exit,
        raise_on_reject: bool,
        service_preinitialized: bool,
        initialize_prompt_accept: bool,
        service_name: str,
        tmpdir,
    ):
        attr_name = f"{service_name}_service"
        svc = getattr(mock_fds_service.service, attr_name)
        fut_name = f"_ensure_{service_name}_initialized"

        hooks_runner = HooksRunner(
            mock_fds_service.service,
            mock_fds_service.printer,
            mock_fds_service.logger,
        )
        fut = getattr(hooks_runner, fut_name)
        mock_prompt.return_value = {"initialize": initialize_prompt_accept}

        with patch.object(
            svc,
            "repo_path",
            tmpdir.strpath,
        ),  patch.object(
            svc,
            "is_initialized",
            return_value=service_preinitialized,
        ), patch.object(
            svc,
            "init",
        ):
            ret = fut()
            assert svc.is_initialized.call_count == 1

            if service_preinitialized:
                assert ret == 0
                return
            assert mock_prompt.call_count == 1

            if initialize_prompt_accept:
                assert svc.init.call_count == 1
                assert ret == 0
                return

            assert re.findall(
                r"You can initialize.*{}.*manually by running".format(service_name),
                mock_fds_service.printer.warn.call_args_list[0].args[0]
            )

            if raise_on_reject:
                assert mock_sys_exit.call_count == 1
            else:
                assert 0 not in mock_sys_exit.called_with

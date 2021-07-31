import os
from dataclasses import dataclass
from enum import Enum
from subprocess import CompletedProcess
from typing import Any, List, Optional, Tuple, Callable
import PyInquirer
from fds.domain.commands import AddCommands
from fds.domain.constants import MAX_THRESHOLD_SIZE
from fds.logger import Logger
from fds.services.pretty_print import PrettyPrint
from fds.services.types import DvcAdd
from fds.utils import get_size_of_path, convert_bytes_to_readable, convert_bytes_to_string, execute_command, \
    append_line_to_file, check_git_ignore, check_dvc_ignore, does_file_exist, \
    construct_dvc_url_from_git_url_dagshub, get_input_from_user


# Choices for DVC
class DvcChoices(Enum):
    ADD_TO_DVC = "Add to DVC"
    ADD_TO_GIT = "Add to Git"
    IGNORE = "Ignore"
    SKIP = "Skip"
    STEP_INTO = "Step Into"


@dataclass
class AddToDvc:
    file_to_add: Optional[str]
    file_to_ignore: Optional[str]
    file_to_skip: Optional[str]


class DVCService(object):
    """
    DVC Service responsible for all the dvc commands of fds
    """

    def __init__(self):
        self.repo_path = os.path.curdir
        self.logger = Logger.get_logger("fds.DVCService")
        self.printer = PrettyPrint()
        self.selection_message_count = 0

    def init(self):
        """
        Responsible for running dvc init
        :return:
        """
        # Check if dvc is already initialized
        if does_file_exist(f"{self.repo_path}/.dvc"):
            return "DVC already initialized"
        execute_command(["dvc", "init", "--subdir"])
        return "DVC initialized successfully"

    def status(self) -> Any:
        """
        Responsible for running dvc status
        :return:
        """
        return execute_command(["dvc", "status"], capture_output=False)

    @staticmethod
    def __should_skip_list_add(directory: str) -> bool:
        """
        Check if the given dir should be skipped or not
        :param directory: the name of the dir
        :return: True if we should skip, else return False
        """
        if directory == ".":
            return True
        git_output = check_git_ignore(directory)
        if convert_bytes_to_string(git_output.stdout) != '':
            return True
        return False

    def __skip_already_added(self, root, dirs) -> None:
        # Check if current file is git ignored (this is very similar to adding to dvc also,
        # because as soon as we add to dvc it gets ignored)
        for d in dirs:
            directory = f"{root}/{d}"
            if self.__should_skip_list_add(directory):
                dirs.remove(d)

    @staticmethod
    def _get_choice(file_or_dir_to_check: str, path_size: int, file_dir_type: str) -> dict:
        choices = [{
            "key": "d",
            "name": "Add to DVC",
            "value": DvcChoices.ADD_TO_DVC.value
        }, {
            "key": "g",
            "name": "Add to Git",
            "value": DvcChoices.ADD_TO_GIT.value
        }, {
            "key": "i",
            "name": "Ignore - Add to .gitignore and .dvcignore",
            "value": DvcChoices.IGNORE.value
        }, {
            "key": "s",
            "name": "Skip - Don't add the file/folder to DVC or Git",
            "value": DvcChoices.SKIP.value
        }]
        if os.path.isdir(file_or_dir_to_check):
            choices.append({
                "key": "s",
                "name": "Step Into",
                "value": DvcChoices.STEP_INTO.value
            })

        questions = [
            {
                "type": "expand",
                "message": f"What would you like to do with {file_dir_type} {file_or_dir_to_check} of "
                           f"{convert_bytes_to_readable(path_size)}?",
                "name": "selection_choice",
                "choices": choices,
                "default": DvcChoices.ADD_TO_DVC.value
            }
        ]
        answers = PyInquirer.prompt(questions)
        return answers

    def __get_to_add_to_dvc(self,
                            file_or_dir_to_check: str,
                            dirs: List[str],
                            file_dir_type: str) -> AddToDvc:
        """
        Returns the tuple (file/folder to be added to dvc, folder to be ignored)
        :param file_or_dir_to_check: File or folder to check if its to be added or ignored
        :param dirs: folders in the current walk
        :param file_dir_type: Type indicating whether its file or Dir
        :return: AddToDvc dataclass
        """
        if not self.__should_skip_list_add(file_or_dir_to_check):
            path_size = get_size_of_path(file_or_dir_to_check)
            # Dont need to traverse deep in case of dir, if the dir is below the threshold size
            if path_size < MAX_THRESHOLD_SIZE:
                if os.path.isdir(file_or_dir_to_check):
                    return AddToDvc(None, file_or_dir_to_check, None)
                return AddToDvc(None, None, None)
            # If the file or dir is greater than threshold and is dvc ignored
            dvc_output = check_dvc_ignore(file_or_dir_to_check)
            if convert_bytes_to_string(dvc_output.stdout) != '':
                return AddToDvc(None, file_or_dir_to_check, None)
            # Show the message only when files are shown and only once per add
            if self.selection_message_count == 0:
                self.selection_message_count = 1
                self.printer.warn('========== Make your selection, Press "h" for help ==========')
            answers = DVCService._get_choice(file_or_dir_to_check=file_or_dir_to_check,
                                             path_size=path_size,
                                             file_dir_type=file_dir_type)
            if answers["selection_choice"] == DvcChoices.ADD_TO_DVC.value:
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return AddToDvc(file_or_dir_to_check, None, None)
            elif answers["selection_choice"] == DvcChoices.ADD_TO_GIT.value:
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return AddToDvc(None, None, None)
            elif answers["selection_choice"] == DvcChoices.SKIP.value:
                # Dont need to traverse deep as we are skipping the folder/file
                [dirs.remove(d) for d in list(dirs)]
                return AddToDvc(None, None, file_or_dir_to_check)
            elif answers["selection_choice"] == DvcChoices.IGNORE.value:
                # We should ignore the ./ in beginning when adding to gitignore
                # Add files to gitignore
                append_line_to_file(".gitignore",
                                    file_or_dir_to_check[file_or_dir_to_check.startswith('./') and 2:])
                # Also add to dvcignore
                append_line_to_file(".dvcignore",
                                    file_or_dir_to_check[file_or_dir_to_check.startswith('./') and 2:])
                # Dont need to traverse deep
                [dirs.remove(d) for d in list(dirs)]
                return AddToDvc(None, None, None)
        return AddToDvc(None, None, None)

    def __add(self, paths_to_be_checked: List[str]) -> DvcAdd:
        chosen_files_or_folders = []
        # Keep track of dirs which are below threshold size, so we dont iterate the files inside these dirs
        ignored_dirs = []
        # Skipped files/folders are those that are not to be tracked by git or dvc and just skipped by the users
        skipped_dirs = []
        # May be add all the folders given in the .gitignore
        folders_to_exclude = ['.git', '.dvc']
        # If . is in paths_to_be_checked then we should iterate through everything
        if AddCommands.ALL.value in paths_to_be_checked:
            paths_to_walk = [self.repo_path]
        else:
            paths_to_walk = list(map(lambda path: f"{self.repo_path}/{path}", paths_to_be_checked))
        for path_to_walk in paths_to_walk:
            # if argument is to add a file
            if os.path.isfile(path_to_walk) and get_size_of_path(path_to_walk) >= MAX_THRESHOLD_SIZE:
                # Keep the file in chosen list
                chosen_files_or_folders.append(path_to_walk)
            for (root, dirs, files) in os.walk(path_to_walk, topdown=True, followlinks=False):
                # Now skip the un-necessary folders
                [dirs.remove(d) for d in list(dirs) if d in folders_to_exclude]
                # Skip the already added files/folders
                self.__skip_already_added(root, dirs)
                # First check root
                add_to_dvc = self.__get_to_add_to_dvc(root, dirs, "Dir")
                if add_to_dvc.file_to_ignore is not None:
                    ignored_dirs.append(add_to_dvc.file_to_ignore)
                if add_to_dvc.file_to_add is not None:
                    chosen_files_or_folders.append(add_to_dvc.file_to_add)
                if add_to_dvc.file_to_skip is not None:
                    skipped_dirs.append(add_to_dvc.file_to_skip)
                else:
                    # Only if they dont select the directory then ask for files,
                    # otherwise ignore asking about files of the directory
                    # We are also showing if the user chooses to skip because the user
                    # might not know there is a large file in the directory and choose skip
                    # because he doesn't want the entire directory to be added.

                    # If the root is skipped because it is below threshold size then we don't need to check files
                    if root in ignored_dirs:
                        continue
                    # If the root is added already then we dont need to scan for files
                    if root in chosen_files_or_folders:
                        continue
                    # Then check files
                    for file in files:
                        add_to_dvc = self.__get_to_add_to_dvc(f"{root}/{file}", [], "File")
                        if add_to_dvc.file_to_ignore is not None:
                            ignored_dirs.append(add_to_dvc.file_to_ignore)
                        if add_to_dvc.file_to_add is not None:
                            chosen_files_or_folders.append(add_to_dvc.file_to_add)
                        if add_to_dvc.file_to_skip is not None:
                            skipped_dirs.append(add_to_dvc.file_to_skip)
        self.logger.debug(f"Chosen folders to be added to dvc are {chosen_files_or_folders}")
        if len(chosen_files_or_folders) > 0:
            self.printer.warn("Adding to dvc...")
            # executing a oneliner for performance
            execute_command(['dvc', 'add'] + chosen_files_or_folders, capture_output=False)
        return DvcAdd(chosen_files_or_folders, skipped_dirs)

    def add(self, paths_to_be_checked: List[str]) -> DvcAdd:
        """
        Add files into dvc
        :param paths_to_be_checked: paths_to_be_checked is a list which can either be ['.'] or list of paths to be checked
        :return: DvcAdd dataclass
        """
        return self.__add(paths_to_be_checked)

    def commit(self, auto_confirm: bool) -> Any:
        """
        Responsible for committing into DVC
        :param auto_confirm: commit all changed files without confirmation
        """
        # In case something is added by user and not committed, we will take care of it
        commit_cmd = ["dvc", "commit", "-q"]
        if auto_confirm:
            commit_cmd.append("-f")
        execute_command(commit_cmd, capture_output=False)

    @staticmethod
    def __execute_push_command(remote: str) -> CompletedProcess:
        push_cmd = ["dvc", "push"]
        # We will only retry once
        if remote:
            push_cmd.append("-r")
            push_cmd.append(remote)
        return execute_command(
            push_cmd,
            capture_output=False,
            capture_output_and_write_to_stdout=True
        )

    def __handle_dagshub_remote(self) -> Tuple[str, str]:
        self.printer.warn("Please enter your credentials, so we can pull from DAGsHub remote")
        user_name = get_input_from_user("Enter your DAGsHub username")
        self.printer.warn("You can navigate to https://dagshub.com/user/settings/tokens to get the token")
        password = get_input_from_user("Enter your DAGsHub token", type="password")
        return user_name, password

    def __handle_dvc_auth(self, remote: str, handler: Callable) -> None:
        output_bytes = handler()
        # Check if its unauthorized
        if '401 Unauthorized' in convert_bytes_to_string(output_bytes.stderr):
            # Check if remote is DagsHub.com
            if "dagshub.com" in remote.lower():
                user_name, password = self.__handle_dagshub_remote()
            else:
                self.printer.warn("Please enter your credentials, so we can pull from your dvc remote")
                user_name = get_input_from_user("Enter your dvc username")
                password = get_input_from_user("Enter your dvc password", type="password")
            dvc_remote_modify=["dvc", "remote", "modify", remote, "--local"]
            # Add auth basic
            execute_command(dvc_remote_modify+["auth", "basic"], capture_output=False)
            # Add username
            execute_command(dvc_remote_modify+["user", user_name], capture_output=False)
            # Add password
            execute_command(dvc_remote_modify+["user", password], capture_output=False)
            # Try to push again
            output_bytes = handler()
            if output_bytes.returncode != 0:
                # Not giving any message because we already print the message in execute_command
                raise Exception()

    def push(self, remote: str) -> Any:
        self.__handle_dvc_auth(remote, lambda: self.__execute_push_command(remote))

    @staticmethod
    def __get_remotes_list() -> dict:
        config_list_cmd = execute_command(["dvc", "remote", "list"], capture_output=True)
        raw_config_list = convert_bytes_to_string(config_list_cmd.stdout).split("\n")
        config_list_dict = {}
        for config_list in raw_config_list:
            remote_name_with_url = config_list.split("\t")
            if (len(remote_name_with_url) == 2):
                config_list_dict[remote_name_with_url[0]] = str(remote_name_with_url[1])
        return config_list_dict

    @staticmethod
    def _show_choice_of_remotes(remotes: dict) -> str:
        choices = list(remotes.keys())
        choices.append("Cancel Pull")
        questions = [
            {
                'type': 'list',
                'name': 'remote',
                'message': 'Choose the remote to use for pulling dvc repo?',
                'choices': choices
            }
        ]
        answers = PyInquirer.prompt(questions)
        return answers["remote"]

    def pull(self, git_url: str, remote_name: Optional[str]) -> Any:
        """
        Responsible for pulling the latest changes from DVC remote based on dvc.yaml and .dvc files
        :param git_url: The git url provided
        :param remote_name: Optional Remote dvc name to pull the dvc repository
        :return:
        """
        self.printer.warn("Staring DVC Clone...")
        if remote_name is None:
            # If nothing is specified
            # First check if its dagshub repo
            if "dagshub.com" in git_url.lower():
                # then construct a dagshub url from the git url
                dvc_url = construct_dvc_url_from_git_url_dagshub(git_url)
                # find it from the remote
                remote_list = DVCService.__get_remotes_list()
                for remote, url in remote_list.items():
                    if url == dvc_url:
                        remote_name = remote
                        break
                if remote_name is None:
                    # if url is not in remote, then add it to remote and use that remote
                    remote_name = "dagshub"
                    execute_command(["dvc", "remote", "add", "--local", remote_name, dvc_url])
            else:
                # If its not dagshub url, then check if there exists a default remote
                default_remote_cmd = execute_command(["dvc", "remote", "default"], capture_output=True)
                default_remote = convert_bytes_to_string(default_remote_cmd.stdout).strip()
                if default_remote == "" or "No default remote set":
                    # No default remote defined
                    # So show all the remotes to user and let user choose
                    remote_list = DVCService.__get_remotes_list()
                    remote_name = DVCService._show_choice_of_remotes(remote_list)
                    # If the user chooses to cancel pull
                    if remote_name not in remote_list:
                        return 0
                else:
                    remote_name = default_remote
        self.__handle_dvc_auth(remote_name, lambda: execute_command(
            ["dvc", "pull", "-r", remote_name],
            capture_output=False,
            capture_output_and_write_to_stdout=True))

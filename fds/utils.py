import getpass
import subprocess
from pathlib import Path
import os
from typing import List, Union, Any, Optional, Dict

import humanize
import select
import sys
from fds.logger import Logger


def get_size_of_path(path: str) -> int:
    if os.path.isdir(path):
        return sum(p.stat().st_size for p in Path(path).rglob('*'))
    else:
        return os.stat(path).st_size


def convert_bytes_to_readable(bytes: int) -> str:
    return humanize.naturalsize(bytes)


def convert_bytes_to_string(bytes_data: bytes) -> str:
    return bytes_data.decode("utf-8")


def execute_command(command: Union[str, List[str]], shell: bool = False, capture_output: bool = True,
                    ignorable_return_codes: List[int] = [0], capture_output_and_write_to_stdout: bool = False) -> Any:
    if capture_output:
        # capture_output is not available in python 3.6, so using PIPE manually
        output = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif capture_output_and_write_to_stdout:
        output = subprocess.Popen(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = []
        stderr = []
        while True:
            reads = [output.stdout.fileno(), output.stderr.fileno()]
            ret = select.select(reads, [], [])

            for fd in ret[0]:
                if fd == output.stdout.fileno():
                    read = output.stdout.readline()
                    sys.stdout.write(convert_bytes_to_string(read))
                    stdout.append(read)
                if fd == output.stderr.fileno():
                    read = output.stderr.readline()
                    sys.stderr.write(convert_bytes_to_string(read))
                    stderr.append(read)
            if output.poll() is not None:
                break
        # create a completed process to have same convention
        return subprocess.CompletedProcess(command, output.returncode, b''.join(stdout), b''.join(stderr))
    else:
        output = subprocess.run(command, shell=shell)
        if output.returncode not in ignorable_return_codes:
            raise Exception(f"Command returned error code {output.returncode}: {command}")
    if output.stderr is None or output.stdout is None:
        return
    logger = Logger.get_logger("fds")
    error_message = convert_bytes_to_string(output.stderr)
    if error_message != '' and output.returncode not in ignorable_return_codes:
        logger.error(error_message)
    if output.returncode not in ignorable_return_codes:
        raise Exception(error_message)
    return output


def rerun_in_new_shell_and_exit(
    cmd: Optional[List[str]] = None
):
    cmd = cmd or ["fds"] + sys.argv

    output = execute_command(
        cmd,
        shell=True,
        capture_output=False,
    )
    sys.exit(output.returncode)


def append_line_to_file(filename: str, data: str) -> None:
    with open(filename, "a") as f:
        f.write(data)
        if not data.endswith('\n'):
            f.write('\n')


def does_file_exist(filename: str) -> bool:
    try:
        import os.path
        return os.path.exists(filename)
    except Exception:
        return False


def check_git_ignore(filename: str) -> Any:
    # You can ignore return code 1 too here, because it shows that the file is not ignored
    # return code 0 is when file is ignored
    git_output = execute_command(["git", "check-ignore", filename], capture_output=True, ignorable_return_codes=[0, 1])
    return git_output


def check_dvc_ignore(filename: str) -> Any:
    # You can ignore return code 1 too here, because it shows that the file is not ignored
    # return code 0 is when file is ignored
    git_output = execute_command(["dvc", "check-ignore", filename], capture_output=True, ignorable_return_codes=[0, 1])
    return git_output


def get_git_repo_name_from_url(url: str) -> str:
    """
    Get the git repository name from the url
    :param url: The git repository url (either https or ssh)
    :return: The repository name
    """
    git_repo_name = url.split("/")[-1]
    return git_repo_name.split(".git")[0]


def construct_dvc_url_from_git_url_dagshub(git_url: str) -> str:
    """
    Construct the dvc url from the git url, given the git url is from DagsHub
    :param git_url: The git url provided
    :return: The dvc url
    """
    return git_url.replace(".git", ".dvc")


def get_input_from_user(question: str, type: str = "input") -> str:
    """
    Get input from user
    :param question: The question to ask user
    :param type: The type of input
    :return: output from the user
    """
    get_input = input
    if type == "password":
        get_input = getpass.getpass
    while True:
        display_text_to_user = f"{question}:"
        answer = get_input(display_text_to_user)
        if answer is not None:
            break
    return answer


def get_expand_input_from_user(
        question: str,
        choices: List[Dict[str, str]],
        default: Union[str, bool, int],
        show_detailed_options: bool
) -> str:
    """
    Get expand input from the user
    :param question: Question to ask the user
    :param choices: List of choices from user
    :param default: Default selected value
    :param show_detailed_options: Show detailed options in first start go
    :return: user selected value
    """

    choices_dict = {x['key'] : x for x in choices}

    def get_display_message(detailed: bool):
        default_key = default_choice["key"]
        display_text_to_user = f"{question}   ({choices_string}) [{default_key}]"
        if detailed or show_detailed_options:
            detailed_choices = [f"{x['key']}) {x['name']}" for x in choices]
            detailed_choices_string = "\n".join(detailed_choices)
            display_text_to_user = f"{display_text_to_user}\n{detailed_choices_string} \nAnswer:"
        return display_text_to_user

    # Only pick choice keys
    choice_keys = list(choices_dict.keys())
    # Add an extra 'h' for help
    choice_keys.append("h")
    choices_string = "".join(choice_keys)
    default_choice = list(filter(lambda x: x['value'] == default, choices))[0]
    input_value = input(get_display_message(detailed=False)) or default_choice["key"]
    help_inputs = {'h', 'help', '?'}
    while True:
        if input_value in choice_keys and input_value not in help_inputs:
            break
        elif input_value in help_inputs:
            # User chose help then we should show the list again with full choices
            input_value = input(get_display_message(detailed=True)) or default_choice["key"]
        else:
            print(f"Not a valid choice: please choose from the given choices ({choices_string})")
            input_value = input(get_display_message(detailed=False)) or default_choice["key"]
    if input_value in choice_keys:
        choice_made = choices_dict[input_value]
        return choice_made["value"]

def get_confirm_from_user(message: str, default: bool) -> bool:
    """
    Get the confirm response from user
    :param message: Message to be shown to user
    :param default: Default value
    :return: User choice of confirm
    """
    choices = [{"key": "y", "value": True, "name": "Yes"}, {"key": "n", "value": False, "name": "No"}]
    return bool(get_expand_input_from_user(message, choices, default, False))


def get_list_choice_from_user(message: str, items_list: List[str]) -> str:
    """
    Get List choice from user
    :param message: Message to be shown to user
    :param list: List value
    :return: User choice of list
    """
    choices = [{"key": i + 1, "value": x, "name": x} for (i, x) in enumerate(items_list)]
    return get_expand_input_from_user(message, choices, 1, True)

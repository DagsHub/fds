import subprocess
from pathlib import Path
import os
from typing import List, Union, Any

import humanize
import select
import sys
from fds.logger import Logger
import PyInquirer

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
        stdout=[]
        stderr=[]
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
            if output.poll() != None:
                break
        # create a completed process to have same convention
        return subprocess.CompletedProcess(command, output.returncode, b''.join(stdout), b''.join(stderr))
    else:
        output = subprocess.run(command, shell=shell)
    if output.stderr is None or output.stdout is None:
        return
    logger = Logger.get_logger("fds")
    error_message = convert_bytes_to_string(output.stderr)
    if error_message != '':
        logger.error(error_message)
    if output.returncode not in ignorable_return_codes:
        raise Exception(error_message)
    return output


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
    questions = [
        {
            'type': type,
            'message': question,
            'name': 'question'
        }
    ]
    answers = PyInquirer.prompt(questions)
    return answers['question']

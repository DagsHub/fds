import argparse
import subprocess
from pathlib import Path
import os
import sys
from typing import List, Union, Any

import humanize

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


def execute_command(command: Union[str, List[str]], shell: bool = False, capture_output: bool=True,
                    ignorable_return_codes: List[int] = [0]) -> Any:
    if capture_output:
        # capture_output is not available in python 3.6, so using PIPE manually
        output = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    except Exception as e:
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

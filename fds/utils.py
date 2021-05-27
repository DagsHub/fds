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
    output = subprocess.run(command, shell=shell, capture_output=capture_output)
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

import argparse
import subprocess
from pathlib import Path
import os
from typing import List, Union, Any

import humanize

from fds.logger import Logger


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_size_of_path(path: str) -> int:
    if os.path.isdir(path):
        return sum(p.stat().st_size for p in Path(path).rglob('*'))
    else:
        return os.stat(path).st_size


def convert_bytes_to_readable(bytes: int) -> str:
    return humanize.naturalsize(bytes)


def convert_bytes_to_string(bytes_data: bytes) -> str:
    return bytes_data.decode("utf-8")


def execute_command(command: Union[str, List[str]], shell: bool = False, capture_output: bool=True) -> Any:
    output = subprocess.run(command, shell=shell, capture_output=capture_output)
    if output.stderr is None or output.stdout is None:
        return
    logger = Logger.get_logger("fds")
    if convert_bytes_to_string(output.stderr) != '':
        logger.error(convert_bytes_to_string(output.stderr))
    return output


def append_line_to_file(filename: str, data: str) -> None:
    with open(filename, "a") as f:
        f.write(data)
        if not data.endswith('\n'):
            f.write('\n')

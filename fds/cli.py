import argparse
import logging
import sys

from fds.logger import Logger

# Argument parser stuff
from fds.run import Run
from fds.utils import str2bool

arg_parser = argparse.ArgumentParser(description="One command for all your git and dvc needs",
                                     prog="fds")
# Command choice
arg_parser.add_argument("command", choices=["init", "status"], help="command (refer commands section in documentation)")

# argument for log level
arg_parser.add_argument("-v", "--verbose", help="set log level to DEBUG",
                    type=str2bool, nargs='?', const=True, default=False)

def parse_args(args):
    arguments = vars(arg_parser.parse_args(args=args or ["--help"]))
    return arguments


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = parse_args(args=args)
    if bool(parsed_args["verbose"]):
        Logger.set_logging_level(logging.DEBUG)
    result = Run(arguments=parsed_args).execute()
    sys.exit(result)


if __name__ == "__main__":
    main()

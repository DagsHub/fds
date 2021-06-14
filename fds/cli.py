import argparse
import logging
import sys

from fds.logger import Logger

# Argument parser stuff
from fds.run import Run
from fds.services.pretty_print import PrettyPrint

arg_parser = argparse.ArgumentParser(description="One command for all your git and dvc needs",
                                     prog="fds")
# Command choice
command_subparser = arg_parser.add_subparsers(dest="command", help="command (refer commands section in documentation)")

# init
parser_init = command_subparser.add_parser('init', help='initialize a git and dvc repository')

# status
parser_status = command_subparser.add_parser('status', help='get status of your git and dvc repository')

# add
parser_add = command_subparser.add_parser('add', help='add files/folders to git and dvc repository')
parser_add.add_argument('add_command', help="choose what to add using . will add everything")

# COMMIT
parser_commit = command_subparser.add_parser('commit', help='commits added changes to git and dvc repository',
                                             conflict_handler='resolve')
parser_commit.add_argument('-y', "--yes",
                           help="Don't ask for confirmation for committing file changes",
                           action="store_true", default=False)
parser_commit_msg_grp = parser_commit.add_mutually_exclusive_group()
parser_commit_msg_grp.add_argument('message', nargs='*', help="commit message", default='')
parser_commit_msg_grp.add_argument('-m', nargs=1, help="commit message", default='')

# push
parser_push = command_subparser.add_parser(
    'push',
    help='push commits to remote git and dvc repository'
)
parser_push.add_argument('-gr', '--git-remote', help="git remote name, default 'origin'", default="origin")
parser_push.add_argument('-dr', '--dvc-remote', help="dvc remote name, default 'origin'", default="origin")
parser_push.add_argument(
    'branch',
    help="A git branch that you want to push to (accepts refspec), defaults to current branch",
    nargs='?'
)
# save
parser_save = command_subparser.add_parser(
    'save',
    help='saves all project files to a new version and pushes them to your remote'
)
parser_save.add_argument('-gr', '--git-remote', help="git remote name, default 'origin'", default="origin")
parser_save.add_argument('-dr', '--dvc-remote', help="dvc remote name, default 'origin'", default="origin")
parser_save.add_argument('message', help="save message")

# argument for log level
arg_parser.add_argument("-v", "--verbose", help="set log level to DEBUG",
                        action="store_true", default=False)


def parse_args(args):
    arguments = vars(arg_parser.parse_args(args=args or ["--help"]))
    return arguments


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    parsed_args = parse_args(args=args)
    printer = PrettyPrint()
    if bool(parsed_args["verbose"]):
        Logger.set_logging_level(logging.DEBUG)
    try:
        result = Run(arguments=parsed_args).execute()
    except Exception as e:
        printer.error(str(e))
        result = 1
    sys.exit(result)


if __name__ == "__main__":
    main()

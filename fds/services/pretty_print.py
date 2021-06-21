from colorama import init
from colorama import Fore


class PrettyPrint(object):

    def __init__(self):
        init(autoreset=True)

    def warn(self, text: str):
        print(Fore.YELLOW + text)

    def log(self, text: str):
        print(Fore.reset + text)

    def error(self, text: str):
        print(Fore.RED + text)

    def success(self, text: str):
        print(Fore.GREEN + text)

    def convert_bytes_to_str(self, bytes_data: bytes) -> str:
        return bytes_data.decode("utf-8")

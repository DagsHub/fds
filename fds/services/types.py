import abc
from dataclasses import dataclass
from typing import List


@dataclass
class DvcAdd:
    files_added_to_dvc: List[str]
    files_skipped: List[str]


class InnerService(abc.ABC):
    repo_path: str

    @abc.abstractmethod
    def is_initialized(self) -> bool:
        pass

    @abc.abstractmethod
    def init(self) -> str:
        pass

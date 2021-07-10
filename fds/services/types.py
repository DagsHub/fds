from dataclasses import dataclass
from typing import List


@dataclass
class DvcAdd:
    files_added_to_dvc: List[str]
    files_skipped: List[str]

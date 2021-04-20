import argparse
from pathlib import Path


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
    return sum(p.stat().st_size for p in Path(path).rglob('*'))

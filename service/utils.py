import traceback
import sys
import os
import time
from typing import Union


def handle_assertion(error: AssertionError) -> str:
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb)
    tb_info = traceback.extract_tb(tb)
    filename, line, _, _ = tb_info[-1]
    return f"An error occurred on {filename}:{line}\n{error}"


def save_to_archives(type: str, basename: str, data: Union[str, bytes]) -> str:
    archive_dir = os.path.join("archives", type)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir, exist_ok=True)
    archive_name = time.strftime(
        "%Y-%m-%d-%H-%M-%S-") + basename
    archive_fullpath = os.path.join(archive_dir, archive_name)
    if isinstance(data, bytes):
        open(archive_fullpath, "wb").write(data)
    else:
        open(archive_fullpath, "w").write(data)
    return archive_fullpath

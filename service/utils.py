import traceback
import sys


def handle_assertion(error: AssertionError) -> str:
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb)
    tb_info = traceback.extract_tb(tb)
    filename, line, _, _ = tb_info[-1]
    return f"An error occurred on {filename}:{line}\n{error}"

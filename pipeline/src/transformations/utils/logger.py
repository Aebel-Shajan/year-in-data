import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import psutil


class ExcludeStringFilter(logging.Filter):
    def __init__(self, excluded_substrings):
        super().__init__()
        self.excluded_substrings = excluded_substrings

    def filter(self, record):
        return not any(
            substring in record.getMessage() for substring in self.excluded_substrings
        )


def get_cpu_memory_usage():
    cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage as a percentage
    memory_info = (
        psutil.Process().memory_info().rss / 1024**2
    )  # Get memory usage details

    return cpu_usage, memory_info


def log_system_resources(logger: logging.Logger):
    cpu, memory = get_cpu_memory_usage()
    logger.info(
        f"{Fore.CYAN + Style.BRIGHT}System Resource Usage\n"
        + "=" * 20
        + "\nCPU".ljust(7)
        + f": {cpu}% "
        + f"\nMemory".ljust(7)
        + f": {memory} MB{Style.RESET_ALL}"
    )


def log_system_resources_regularly(logger: logging.Logger, interval=5):
    while True:
        log_system_resources(logger)
        time.sleep(interval)


def add_date_file_handler(
    logger: logging.Logger,
    log_dir: str = "logs",
    base_filename: str = "pipeline",
    formatter_to_override: logging.Logger = logging.Formatter(),
):
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Generate log filename: pipeline_YYYY-MM-DD.log
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{base_filename}_{date_str}.log"

    # Avoid duplicate handlers for the same file
    if not any(
        isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file)
        for h in logger.handlers
    ):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(NonColoredFormatter(formatter_to_override))
        logger.addHandler(file_handler)


# Other utils
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ""

    def write(self, message):
        self.buffer += message
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():
                self.logger.log(self.level, line)

    def flush(self):
        if self.buffer.strip():
            self.logger.log(self.level, self.buffer.strip())
        self.buffer = ""


@contextmanager
def redirect_output_to_logger(
    logger: logging.Logger,
    stdout_level: int | None = None,
    stderr_level: int | None = None,
    name: str | None = None,
):
    """Redirect sys.stdout and sys.stderr to the given logger.

    Args:
        logger: A logging.Logger instance.
        stdout_level: Logging level for stdout (e.g., logging.INFO).
        stderr_level: Logging level for stderr (e.g., logging.ERROR).
        name: Optional name to temporarily assign to the logger.
    """
    old_name = logger.name

    logger.name = name or old_name
    stdout_level = stdout_level or logging.INFO
    stderr_level = stderr_level or logging.ERROR

    stdout_logger = StreamToLogger(logger, stdout_level)
    stderr_logger = StreamToLogger(logger, stderr_level)

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    sys.stdout = stdout_logger
    sys.stderr = stderr_logger

    try:
        yield
    finally:
        logger.name = old_name
        sys.stdout = old_stdout
        sys.stderr = old_stderr

import logging
import re
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import psutil
from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
init(autoreset=True)

# Define color mappings for different log levels
LOG_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, show_context=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_context = show_context

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Overrides basic formatMessage method. Uses colorama to output fancy colored text.

        Args:
            record (LogRecord): The log record containing all the information for the log entry.

        Returns:
            string: A formatted log message with colors and structured layout.

        Notes:
            Why not override just the `logging.Formatter.format()` method?
            See the following link:
            https://github.com/python/cpython/blob/7dddb4e667b5eb76cbe11755051ec139b0f437a9/Lib/logging/__init__.py#L682-L729
            Overriding format also overrides some which prints out exception
            traceback.
        """
        log_color = LOG_COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL

        # Define fixed column widths
        datefmt_length = 8
        if len(self.datefmt) > 8:
            datefmt_length = 20
        timestamp = self.formatTime(record, self.datefmt).ljust(
            datefmt_length
        )  # Timestamp column (fixed width)
        level = record.levelname.ljust(8)  # Log level column (fixed width)
        context = record.name
        message = record.getMessage()  # Log message (variable width)

        header = f"{log_color}{timestamp}{reset} | {log_color}{level}{reset} | "
        if self.show_context:
            header += f"{log_color}{context}{reset}: "

        if "\n" in message:
            header_length = datefmt_length + 3 + 8
            indent = " " * header_length + " |"
            if self.show_context:
                indent += " " * (len(context) + 2)
            message = f"\n{indent}  ".join(message.splitlines())

        # Format final log output
        log_message = header + f"{message}"
        return log_message


class NonColoredFormatter(logging.Formatter):
    def __init__(self, formatter_to_override: logging.Formatter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter_to_override = formatter_to_override

    def formatMessage(self, record):
        message = self.formatter_to_override.formatMessage(record)
        ansi_re = re.compile(r"\x1b\[[0-9;]*m")
        return re.sub(ansi_re, "", message)


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


def setup_aebels_logger(
    logger: logging.Logger,
    filter_strings: list[str] = [],
    resource_monitoring_interval: float = -1,
    show_context: bool = True,
    date_fmt: str = "%H:%M:%S",
    log_file_prefix: str = "pipeline_run",
):

    colored_formatter = ColoredFormatter(
        show_context=show_context,
        datefmt=date_fmt,
    )
    # Modify existing handlers on logger to user colored formattedr
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            # Define a formatter with equal-width columns

            handler.setFormatter(colored_formatter)
            handler.addFilter(ExcludeStringFilter(filter_strings))

    add_date_file_handler(
        logger,
        base_filename=log_file_prefix,
        formatter_to_override=colored_formatter,
    )

    if resource_monitoring_interval > 1:
        # Create and start the background thread for resource logging
        resource_thread = threading.Thread(
            target=log_system_resources_regularly,
            args=(logger, resource_monitoring_interval),
            daemon=True,
        )
        resource_thread.start()


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

import logging
import sys
import threading
import time
from colorama import Fore, Style, init
import sys
from contextlib import contextmanager

import psutil

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
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL

        # Define fixed column widths
        timestamp = self.formatTime(record, self.datefmt).ljust(20)  # Timestamp column (fixed width)
        level = record.levelname.ljust(8)  # Log level column (fixed width)
        context = record.name
        message = record.getMessage()  # Log message (variable width)

        # Format final log output
        log_message = f"{log_color}{timestamp}{reset} | {log_color}{level}{reset} | {log_color}{context}{reset}: {message}"
        return log_message
 
 
class ExcludeStringFilter(logging.Filter):
    def __init__(self, excluded_substrings):
        super().__init__()
        self.excluded_substrings = excluded_substrings

    def filter(self, record):
        return not any(
            substring in record.getMessage() 
            for substring in self.excluded_substrings
        )   
        
    
def get_cpu_memory_usage():
    cpu_usage = psutil.cpu_percent(interval=1)  # Get CPU usage as a percentage
    memory_info = psutil.Process().memory_info().rss/ 1024 ** 2  # Get memory usage details

    return cpu_usage, memory_info


def log_system_resources(logger, interval=5):
    while True:
        cpu, memory = get_cpu_memory_usage()
        logger.info(
            f"{Fore.CYAN + Style.BRIGHT}System Resource Usage | "
            f"CPU: {cpu}% | "
            f"Memory: {memory} MB{Style.RESET_ALL}"
        )
        time.sleep(interval)

        
def setup_aebels_logger(
    logger: logging.Logger,
    filter_strings: list[str] = [],
    resource_monitoring_interval: float = -1
):
    # Modify existing handlers on logger to user colored formattedr
    for handler in logger.handlers:
        # Define a formatter with equal-width columns
        formatter = ColoredFormatter(datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        handler.addFilter(ExcludeStringFilter(filter_strings))
    
    
    if resource_monitoring_interval > 1:
        # Create and start the background thread for resource logging
        resource_thread = threading.Thread(
            target=log_system_resources,
            args=(logger, resource_monitoring_interval),
            daemon=True,
        )
        resource_thread.start()


# Other utils
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = ''

    def write(self, message):
        self.buffer += message
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            if line.strip():
                self.logger.log(self.level, line)

    def flush(self):
        if self.buffer.strip():
            self.logger.log(self.level, self.buffer.strip())
        self.buffer = ''


@contextmanager
def redirect_output_to_logger(
    logger: logging.Logger, 
    stdout_level: int | None = None, 
    stderr_level: int | None = None, 
    name: str | None  = None,
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
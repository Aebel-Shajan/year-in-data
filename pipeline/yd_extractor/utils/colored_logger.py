import logging
import sys
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
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL

        # Define fixed column widths
        timestamp = self.formatTime(record, self.datefmt).ljust(20)  # Timestamp column (fixed width)
        level = record.levelname.ljust(8)  # Log level column (fixed width)
        message = record.getMessage()  # Log message (variable width)

        # Format final log output
        log_message = f"{log_color}{timestamp}{reset} | {log_color}{level}{reset} | {message}"
        return log_message
    
    
def setup_colored_logger(logger: logging.Logger):
    # Create a console handler
    for handler in logger.handlers:
        # Define a formatter with equal-width columns
        formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

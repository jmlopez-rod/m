import logging
import sys


class StdErrHandler(logging.StreamHandler):
    """A log handler to print to stderr."""

    def __init__(self, formatter: logging.Formatter):
        """Initialize the handler.

        Args:
            formatter: The formatter to use with the handler.
        """
        super().__init__(sys.stderr)
        self.setFormatter(formatter)

    def filter(self, record: logging.LogRecord) -> bool:
        """Only display warnings or error records.

        Args:
            record: A logging record instance.

        Returns:
            True if the record is a warning or error.
        """
        return record.levelno >= logging.WARNING


class StdOutHandler(logging.StreamHandler):
    """A log handler to print to stdout."""

    def __init__(self, formatter: logging.Formatter):
        """Initialize the handler.

        Args:
            formatter: The formatter to use with the handler.
        """
        super().__init__(sys.stdout)
        self.setFormatter(formatter)

    def filter(self, record: logging.LogRecord) -> bool:
        """Display non-warnings and non-error records.

        Args:
            record: A logging record instance.

        Returns:
            True if the record is not a warning or error.
        """
        return record.levelno < logging.WARNING

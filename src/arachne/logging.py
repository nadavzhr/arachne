"""Central logging configuration for Arachne."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(spider_name)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_SAFE_SPIDER_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


class SpiderFormatter(logging.Formatter):
    """Formatter that ensures all log records have a `spider_name` attribute.

    This ensures that logs from outside of spider contexts (e.g., core services)
    can still be processed by the SpiderFileHandler without errors.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as text.

        Args:
            record: The log record to format.

        Returns:
            str: The formatted log record.
        """
        if not hasattr(record, "spider_name"):
            record.spider_name = "-"
        return super().format(record)


class SpiderFileHandler(logging.Handler):
    """Handler that routes log records into per-spider files.

    Records with a valid `spider_name` (not empty or '-') are written to a
    specific log file in the configured spider log directory.
    """

    def __init__(self, root: Path) -> None:
        """Initialize the handler.

        Args:
            root: Path to the directory where spider logs should be stored.
        """
        super().__init__()
        self.root = root
        self._handlers: dict[str, logging.FileHandler] = {}

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record.

        Args:
            record: The log record to emit.
        """
        spider_name = getattr(record, "spider_name", "")
        if not isinstance(spider_name, str) or not spider_name or spider_name == "-":
            return
        try:
            self._handler_for(spider_name).emit(record)
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        for handler in self._handlers.values():
            handler.close()
        self._handlers.clear()
        super().close()

    def _handler_for(self, spider_name: str) -> logging.FileHandler:
        safe_name = _SAFE_SPIDER_RE.sub("_", spider_name).strip("._") or "unknown"
        if safe_name not in self._handlers:
            self.root.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(
                self.root / f"{safe_name}.log",
                mode="w",
                encoding="utf-8",
            )
            handler.setLevel(self.level)
            handler.setFormatter(self.formatter)
            self._handlers[safe_name] = handler
        return self._handlers[safe_name]


def timestamped_log_name(filename: str, stamp: str) -> str:
    """Append a timestamp to a filename while preserving the extension.

    Args:
        filename: The original filename (e.g., 'arachne.log').
        stamp: The timestamp string to append.

    Returns:
        str: The timestamped filename (e.g., 'arachne-20240101.log').
    """
    path = Path(filename)
    suffix = path.suffix
    if suffix:
        return f"{path.stem}-{stamp}{suffix}"
    return f"{path.name}-{stamp}"


def configure_logging(
    *,
    enabled: bool,
    directory: str | Path,
    level: str,
    central_file: str,
    spider_directory: str,
    console_enabled: bool = False,
) -> int:
    """Initialize the application's logging subsystem.

    This configures a central log file, isolated per-spider log files, and
    optional console output via Rich.

    Args:
        enabled: Whether file logging is enabled.
        directory: Root directory for all logs.
        level: The global log level (e.g., 'INFO').
        central_file: Filename for the combined log file.
        spider_directory: Subdirectory for per-spider log files.
        console_enabled: Whether to output logs to the console.

    Returns:
        int: The numeric log level that was configured.
    """

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    log_level = logging.getLevelName(level.upper())
    if not isinstance(log_level, int):
        log_level = logging.INFO

    if not enabled and not console_enabled:
        root_logger.addHandler(logging.NullHandler())
        return log_level

    formatter = SpiderFormatter(_DEFAULT_FORMAT, datefmt=_DATE_FORMAT)
    root_logger.setLevel(log_level)

    if enabled:
        log_dir = Path(directory)
        log_dir.mkdir(parents=True, exist_ok=True)
        spider_log_dir = log_dir / spider_directory
        central_log_path = log_dir / central_file

        central_handler = logging.FileHandler(central_log_path, mode="w", encoding="utf-8")
        central_handler.setLevel(log_level)
        central_handler.setFormatter(formatter)

        spider_handler = SpiderFileHandler(spider_log_dir)
        spider_handler.setLevel(log_level)
        spider_handler.setFormatter(formatter)

        root_logger.addHandler(central_handler)
        root_logger.addHandler(spider_handler)

    if console_enabled:
        from rich.logging import RichHandler

        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            omit_repeated_times=False,
        )
        # Use a simpler format for console to avoid double timestamps from Rich
        console_handler.setFormatter(logging.Formatter("[%(spider_name)s] %(message)s"))
        root_logger.addHandler(console_handler)

    logging.captureWarnings(True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return log_level


def spider_logger(spider_name: str, logger_name: str) -> logging.LoggerAdapter[Any]:
    """Return a logger adapter that injects the spider name into log records.

    Args:
        spider_name: The name of the spider to associate with logs.
        logger_name: The name of the logger to wrap (typically `__name__`).

    Returns:
        logging.LoggerAdapter: An adapter that automatically adds 'spider_name'.
    """

    return logging.LoggerAdapter(
        logging.getLogger(logger_name),
        {"spider_name": spider_name or "unknown"},
    )

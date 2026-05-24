"""Central logging configuration for Arachne."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(source_name)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_SAFE_SOURCE_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


class SourceFormatter(logging.Formatter):
    """Formatter that gives non-source records a stable source field."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "source_name"):
            record.source_name = "-"
        return super().format(record)


class SourceFileHandler(logging.Handler):
    """Route records with ``source_name`` into per-source log files."""

    def __init__(self, root: Path) -> None:
        super().__init__()
        self.root = root
        self._handlers: dict[str, logging.FileHandler] = {}

    def emit(self, record: logging.LogRecord) -> None:
        source_name = getattr(record, "source_name", "")
        if not isinstance(source_name, str) or not source_name or source_name == "-":
            return
        try:
            self._handler_for(source_name).emit(record)
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        for handler in self._handlers.values():
            handler.close()
        self._handlers.clear()
        super().close()

    def _handler_for(self, source_name: str) -> logging.FileHandler:
        safe_name = _SAFE_SOURCE_RE.sub("_", source_name).strip("._") or "unknown"
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
    """Append a timestamp to a filename while preserving the extension."""
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
    source_directory: str,
    console_enabled: bool = False,
) -> int:
    """Configure logging for the application.

    Returns the numeric log level configured.
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

    formatter = SourceFormatter(_DEFAULT_FORMAT, datefmt=_DATE_FORMAT)
    root_logger.setLevel(log_level)

    if enabled:
        log_dir = Path(directory)
        log_dir.mkdir(parents=True, exist_ok=True)
        source_log_dir = log_dir / source_directory
        central_log_path = log_dir / central_file

        central_handler = logging.FileHandler(central_log_path, mode="w", encoding="utf-8")
        central_handler.setLevel(log_level)
        central_handler.setFormatter(formatter)

        source_handler = SourceFileHandler(source_log_dir)
        source_handler.setLevel(log_level)
        source_handler.setFormatter(formatter)

        root_logger.addHandler(central_handler)
        root_logger.addHandler(source_handler)

    if console_enabled:
        from rich.logging import RichHandler

        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            omit_repeated_times=False,
        )
        # Use a simpler format for console to avoid double timestamps from Rich
        console_handler.setFormatter(logging.Formatter("[%(source_name)s] %(message)s"))
        root_logger.addHandler(console_handler)

    logging.captureWarnings(True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return log_level


def source_logger(source_name: str, logger_name: str) -> logging.LoggerAdapter[Any]:
    """Return a logger adapter that marks records with the source name."""

    return logging.LoggerAdapter(
        logging.getLogger(logger_name),
        {"source_name": source_name or "unknown"},
    )

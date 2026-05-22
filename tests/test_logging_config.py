import logging
from pathlib import Path

from arachne.logging_config import configure_logging, source_logger


def _flush_handlers() -> None:
    for handler in logging.getLogger().handlers:
        handler.flush()


def test_configure_logging_writes_central_and_source_logs(tmp_path: Path) -> None:
    configure_logging(
        enabled=True,
        directory=tmp_path,
        level="INFO",
        central_file="arachne.log",
        source_directory="sources",
    )

    logging.getLogger("arachne.test").info("application message")
    source_logger("microsoft", "arachne.test").info("source message")
    _flush_handlers()

    central_log = tmp_path / "arachne.log"
    source_log = tmp_path / "sources" / "microsoft.log"

    assert "application message" in central_log.read_text(encoding="utf-8")
    assert "source message" in central_log.read_text(encoding="utf-8")
    assert "source message" in source_log.read_text(encoding="utf-8")
    assert "application message" not in source_log.read_text(encoding="utf-8")


def test_disabled_logging_installs_no_file_handlers(tmp_path: Path) -> None:
    configure_logging(
        enabled=False,
        directory=tmp_path,
        level="INFO",
        central_file="arachne.log",
        source_directory="sources",
    )

    source_logger("microsoft", "arachne.test").info("source message")
    _flush_handlers()

    assert not (tmp_path / "arachne.log").exists()

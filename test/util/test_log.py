from pathlib import Path
from typing import Iterator

import pytest

from app.util.log import Logger

# pylint: disable=protected-access


@pytest.fixture
def cleanup_log_files() -> Iterator[None]:
    """清理测试时产生的日志文件"""
    yield

    Logger.stop_logging()
    for file in Path("logs").iterdir():
        if file.is_file and file.name.endswith(".log"):
            file.unlink()


class TestLogger:
    def test_init(self) -> None:
        with pytest.raises(
            RuntimeError, match=r"This class is not meant to be instantiated"
        ):
            Logger()

    @pytest.mark.usefixtures("cleanup_log_files")
    def test_start_logging(self) -> None:
        Logger.start_logging()
        before: int | None = Logger._log_handler_id

        Logger.start_logging()
        after: int | None = Logger._log_handler_id

        assert before is not None
        assert before == after

    @pytest.mark.usefixtures("cleanup_log_files")
    def test_stop_logging(self) -> None:
        assert Logger._log_handler_id is None

        Logger.start_logging()
        assert Logger._log_handler_id is not None

        Logger.stop_logging()
        assert Logger._log_handler_id is None

        Logger.stop_logging()  # test stop_logging when already stopped
        assert Logger._log_handler_id is None

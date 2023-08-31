from typing import NoReturn, Optional

from loguru import logger

from app.util.settings import Settings, SettingsManager


# TODO(batu1579): 添加更多的日志处理器，分级处理不同的问题
class Logger:
    _log_handler_id: Optional[int] = None

    def __init__(self) -> NoReturn:
        raise RuntimeError("This class is not meant to be instantiated")

    @classmethod
    def start_logging(cls) -> None:
        """开始记录日志"""
        if cls._log_handler_id is not None:
            return

        settings: Settings = SettingsManager.get_settings()
        cls._log_handler_id = logger.add(
            sink="logs/log.log",
            enqueue=True,
            rotation=settings.log.rotation,
            retention=settings.log.retention,
            compression="tar.gz",
        )

    @classmethod
    def stop_logging(cls) -> None:
        """停止记录日志"""
        logger.info("Shutting down...")

        if cls._log_handler_id is None:
            return

        logger.remove(cls._log_handler_id)
        cls._log_handler_id = None

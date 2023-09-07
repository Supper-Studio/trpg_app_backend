from pathlib import Path
from typing import NoReturn, Optional

from loguru import logger
from pydantic import (
    BaseModel,
    Field,
    FieldValidationInfo,
    MongoDsn,
    RedisDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class _BaseSettings(BaseModel):
    model_config = SettingsConfigDict(frozen=True)


class _ServiceSettings(_BaseSettings):
    host: str = Field(default="localhost", title="Service host")
    port: int = Field(default=8000, title="Service port")
    origins: list[str] = Field(default=["localhost"], title="List of trusted domains")
    gzip_min_size: int = Field(default=500, title="Gzip min size")


class _SSLSettings(_BaseSettings):
    keyfile: Optional[Path] = Field(default=None, title="Path to SSL key file")
    certfile: Optional[Path] = Field(default=None, title="Path to SSL certificate file")
    redirect: bool = Field(default=False, title="Redirect all requests to HTTPS")

    @field_validator("keyfile", "certfile", mode="before")
    @classmethod
    def convert_relative_path(
        cls, path_str: Optional[str], info: FieldValidationInfo
    ) -> Optional[Path]:
        """将相对文件路径转换为绝对路径

        Args:
            path_str (Optional[str]): 文件路径

        Returns:
            Optional[Path]: 绝对文件路径（当传入为 None 时也返回 None ）。
        """
        if path_str is None:
            return None

        path = Path(path_str).absolute()

        if not path.is_file():
            logger.warning(
                f"{info.field_name} '{path.as_uri()}' does not exist "
                + "or is not a regular file. "
                + "Please check the file or settings."
            )

            return None

        return path

    @field_validator("redirect")
    @classmethod
    def validate_ssl_files(cls, need_redirect: bool, info: FieldValidationInfo) -> bool:
        """校验 SSL 证书文件

        Args:
            need_redirect (bool): 是否重定向到 https
            info (FieldValidationInfo): 模型信息

        Returns:
            bool: 是否重定向到 https
        """
        if not need_redirect:
            return False

        keyfile: Path | None = info.data.get("keyfile")
        certfile: Path | None = info.data.get("certfile")

        if (keyfile is None) or (certfile is None):
            logger.warning(
                "If you want to enable https redirection, "
                + "you need to ensure that both keyfile and certfile are valid files. "
                + "Now https redirection will be disabled."
            )
            return False

        return True


class _DatabaseSettings(_BaseSettings):
    mongo_url: MongoDsn = Field(
        default=...,
        title="Mongo database URL",
        examples=[MongoDsn("mongodb://username:password@localhost:27017/")],
    )
    redis_url: RedisDsn = Field(
        default=...,
        title="Redis database URL",
        examples=[RedisDsn("redis://username:password@localhost:6379/1")],
    )


class _DocumentSettings(_BaseSettings):
    docs_path: str = Field(
        default="/docs",
        title="Document URL",
    )
    redoc_path: str = Field(default="/redocs", title="Redocs URL")


class _LogSettings(_BaseSettings):
    rotation: str = Field(
        default="200 MB",
        title="日志分隔方式",
        examples=[
            "0.5 GB",
            "200 MB",
            "4 days",
            "10 h",
            "18:00",
            "sunday",
            "monday at 12:00",
        ],
    )
    retention: str | int = Field(
        default=10,
        title="日志保留方式",
        examples=[
            10,
            "1 week, 3 days",
            "2 months",
        ],
    )

    @field_validator("retention")
    @classmethod
    def check_retention(cls, retention: str | int) -> str | int:
        """校验日志文件保存设置

        Args:
            retention (str | int): 日志保留方式

        Returns:
            str | int: 将纯数字的字符串转换为整数
        """
        if isinstance(retention, str):
            if not retention.isdigit():
                return retention
            retention = int(retention)

        if retention < 0:
            logger.warning(
                "Log file retention must be positive. "
                + "Now retention will set to zero"
            )
            return 0

        return retention


class _IDServiceSettings(_BaseSettings):
    host: str = Field(default="localhost", title="ID Service host")
    port: int = Field(default=3306, title="ID Service port")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        env_nested_delimiter="__",
        frozen=True,
    )

    service: _ServiceSettings = Field(
        default=_ServiceSettings(), title="Service settings"
    )
    ssl: _SSLSettings = Field(
        default=_SSLSettings(),
        title="SSL settings",
    )
    database: _DatabaseSettings = Field(
        default=...,
        title="Database settings",
    )
    document: _DocumentSettings = Field(
        default=_DocumentSettings(),
        title="Document settings",
    )
    log: _LogSettings = Field(
        default=_LogSettings(),
        title="Log settings",
    )
    id_service: _IDServiceSettings = Field(
        default=_IDServiceSettings(),
        title="ID Service settings",
    )


class SettingsManager:
    _env_file_path: Optional[Path] = Path(".env")
    _settings_instance: Optional[Settings] = None

    def __init__(self) -> NoReturn:
        raise RuntimeError(
            "This class is a singleton! Please use get_settings() instead."
        )

    @classmethod
    def set_env_file_path(cls, env_file_path: Optional[Path]) -> bool:
        """设置读取 .env 文件的路径

        Args:
            env_file_path (Optional[Path]): 具体的文件路径，如果为 None 则不从文件读取

        Returns:
            bool: 是否设置成功，如果设置失败，则返回 False
        """
        if env_file_path is None:
            cls._env_file_path = None
            return True

        env_file_path = env_file_path.absolute()

        if not env_file_path.is_file():
            logger.warning(
                f"Environment file '{env_file_path.as_uri()}' does not exist "
                + "or is not a regular file. "
                + "Please check the file or settings."
            )
            return False

        cls._env_file_path = env_file_path
        return True

    @classmethod
    def get_settings(cls) -> Settings:
        """单例模式获取设置项实例，保证全局统一

        Returns:
            Settings: 设置项实例
        """
        if cls._settings_instance is None:
            cls._settings_instance = Settings(
                _env_file=cls._env_file_path  # type: ignore
            )
        return cls._settings_instance

    @classmethod
    def reload_settings(cls) -> None:
        """删除设置模型实例以便于重新加载"""
        cls._settings_instance = None

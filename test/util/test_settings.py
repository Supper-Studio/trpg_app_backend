from pathlib import Path

import pytest

from app.util.settings import Settings, SettingsManager, _LogSettings, _SSLSettings

# pylint: disable=protected-access


class TestSSLSettings:
    def test_convert_relative_path(self, not_existing_file: Path) -> None:
        ssl_settings = _SSLSettings(
            keyfile=not_existing_file,
            certfile=None,
            redirect=True,
        )
        assert ssl_settings.keyfile is None
        assert ssl_settings.certfile is None
        assert ssl_settings.redirect is False

    def test_validate_ssl_files(self, temp_file: Path) -> None:
        ssl_settings = _SSLSettings(
            keyfile=temp_file,
            certfile=temp_file,
            redirect=True,
        )

        keyfile: Path | None = ssl_settings.keyfile
        assert keyfile is not None
        assert keyfile.is_absolute()  # pylint: disable=no-member

        certfile: Path | None = ssl_settings.certfile
        assert certfile is not None
        assert certfile.is_absolute()  # pylint: disable=no-member

        assert ssl_settings.redirect is True


class TestLogSettings:
    def test_check_retention(self) -> None:
        log_settings = _LogSettings(retention=-1)
        assert log_settings.retention == 0

        log_settings = _LogSettings(retention="20")
        assert log_settings.retention == 20

        log_settings = _LogSettings(retention="1 days")
        assert log_settings.retention == "1 days"


@pytest.fixture
def env_file_example() -> Path:
    """使用示例 env 文件

    Returns:
        Path: .env.example 文件路径
    """
    return Path(".env.example")


class TestSettingsManager:
    def test_init(self) -> None:
        with pytest.raises(RuntimeError, match=r"This class is a singleton"):
            SettingsManager()

    def test_set_env_file_path(
        self,
        not_existing_file: Path,
        not_existing_directory: Path,
        env_file_example: Path,
    ) -> None:
        assert not SettingsManager.set_env_file_path(not_existing_directory)
        assert not SettingsManager.set_env_file_path(not_existing_file)

        assert SettingsManager.set_env_file_path(env_file_example)
        assert SettingsManager._env_file_path == env_file_example.absolute()

        assert SettingsManager.set_env_file_path(None)
        assert SettingsManager._env_file_path is None

    def test_get_settings(self, env_file_example: Path) -> None:
        SettingsManager.set_env_file_path(env_file_example)
        before: Settings = SettingsManager.get_settings()
        after: Settings = SettingsManager.get_settings()
        assert id(before) == id(after)

    def test_reload_settings(self) -> None:
        before: Settings = SettingsManager.get_settings()

        SettingsManager.reload_settings()
        assert SettingsManager._settings_instance is None

        after: Settings = SettingsManager.get_settings()
        assert id(before) != id(after)

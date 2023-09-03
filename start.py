from pathlib import Path
from typing import Optional

from pydantic import validate_call
from typer import Option, Typer
from uvicorn import run as uvicorn_run

from app.util.settings import Settings, SettingsManager

cli = Typer(help="TRPG App server")


@cli.command()
@validate_call
def run(env_file: Optional[Path] = Option(None, help="手动指定环境变量文件位置")) -> None:
    """启动服务"""
    if env_file is not None:
        SettingsManager.set_env_file_path(env_file)
    SettingsManager.reload_settings()

    settings: Settings = SettingsManager.get_settings()

    keyfile_path: Path | None = settings.ssl.keyfile
    certfile_path: Path | None = settings.ssl.certfile

    uvicorn_run(
        app="app.main:create_app",
        host=settings.service.host,
        port=settings.service.port,
        ssl_keyfile=keyfile_path.as_posix() if keyfile_path else None,
        ssl_certfile=certfile_path.as_posix() if certfile_path else None,
        factory=True,
    )


@cli.command()
@validate_call
def test() -> None:
    """运行服务测试"""
    print("Start testing...")


if __name__ == "__main__":
    cli()

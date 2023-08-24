from pathlib import Path
from typing import Optional

from pydantic import validate_call
from typer import Option, Typer
from uvicorn import run as uvicorn_run

app = Typer(help="TRPG App server")


@app.command()
@validate_call
def run(env_file: Optional[Path] = Option(None, help="手动指定环境变量文件位置")):
    """启动服务"""
    uvicorn_run(
        app="app.main:app",
        host=SETTINGS.service.host,
        port=SETTINGS.service.port,
        ssl_keyfile=keyfile_path,
        ssl_certfile=certfile_path,
    )


if __name__ == "__main__":
    app()

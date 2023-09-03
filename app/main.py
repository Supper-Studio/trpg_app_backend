from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.util.log import Logger
from app.util.settings import Settings, SettingsManager


def create_app() -> FastAPI:
    """初始化 FastAPI 应用，加载中间件并注册处理器

    Returns:
        FastAPI: 给 uvicorn 启动服务用的应用对象
    """
    settings: Settings = SettingsManager.get_settings()

    app = FastAPI(
        title="TRPG APP API",
        version="0.1.0",
        docs_url=settings.document.docs_path,
        redoc_url=settings.document.redoc_path,
    )

    # 注册中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.service.origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.service.gzip_min_size,
    )

    if settings.ssl.redirect:
        app.add_middleware(HTTPSRedirectMiddleware)

    # 注册事件
    app.add_event_handler("startup", Logger.start_logging)

    app.add_event_handler("shutdown", Logger.stop_logging)

    return app

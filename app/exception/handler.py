from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import HttpUrl

from app.exception.error_code import ErrorInfo
from app.exception.error_code.outer_error import (
    INVALID_ARGUMENT_ERROR_CODE,
    UNKNOWN_ERROR_CODE,
)
from app.exception.known_exception import KnownException
from app.model.response import Error


def invaild_argument_handler(
    _req: Request, _exc: RequestValidationError
) -> JSONResponse:
    """非法请求参数异常处理器

    Args:
        _req (Request): 请求原文
        _exc (RequestValidationError): 引发的异常对象

    Returns:
        JSONResponse: 响应数据
    """
    error_info = ErrorInfo(
        code=INVALID_ARGUMENT_ERROR_CODE,
        detail=_exc.errors(),
        help="Check out the wrong request parameters in detail field.",
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            Error(
                message="Invalid request, please check your request parameters",
                error=error_info,
            ),
            exclude_none=True,
        ),
    )


def known_error_handler(_req: Request, _exc: KnownException) -> JSONResponse:
    """已知的错误处理器

    Args:
        _req (Request): 请求原文
        _exc (KnownException): 引发的异常对象

    Returns:
        JSONResponse: 响应数据
    """
    return JSONResponse(
        status_code=_exc.status_code,
        content=jsonable_encoder(
            Error(
                message=_exc.message,
                error=_exc.error_info,
            ),
            exclude_none=True,
        ),
    )


def http_exception_handler(_req: Request, _exc: HTTPException) -> JSONResponse:
    """HTTP 异常处理器

    Args:
        _req (Request): 请求原文
        _exc (HTTPException): 引发的异常对象

    Returns:
        JSONResponse: 响应数据
    """
    error_info = ErrorInfo(
        code=UNKNOWN_ERROR_CODE,
        detail=_exc.detail,
        help="Please report this to the developers and try again later.",
        document_url=HttpUrl(
            "https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status"
        ),
    )

    logger.error(f"HTTP exception occurred: {_exc}")

    return JSONResponse(
        status_code=_exc.status_code,
        content=jsonable_encoder(
            Error(
                message="An HTTP exception occurred",
                error=error_info,
            ),
            exclude_none=True,
        ),
    )


def general_exception_handler(_req: Request, _exc: Exception) -> JSONResponse:
    """其他异常通用处理器

    Args:
        _req (Request): 请求原文
        _exc (Exception): 引发的异常对象

    Returns:
        JSONResponse: 响应数据
    """
    error_info = ErrorInfo(
        code=UNKNOWN_ERROR_CODE,
        detail=_exc,
        help="Please report this to the developers and try again later.",
    )

    logger.error(f"Unknown exception occurred: {_exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            Error(
                message="Unknown server exception occurred",
                error=error_info,
            ),
            exclude_none=True,
        ),
    )

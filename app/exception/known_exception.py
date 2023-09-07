from typing import Any, Optional

from fastapi import HTTPException, status

from app.exception.error_code.error_model import ErrorInfo


class KnownException(HTTPException):
    message: str
    error_info: ErrorInfo

    def __init__(
        self,
        message: str,
        error_info: ErrorInfo,
        *,
        status_code: Optional[int] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.error_info = error_info

        super().__init__(
            status_code=status_code or status.HTTP_400_BAD_REQUEST,
            headers=headers,
        )

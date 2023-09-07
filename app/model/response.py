from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from app.exception import ErrorInfo


class ResponseStatus(int, Enum):
    OK = 0
    ERROR = 1


class JsonResponseModel(BaseModel):
    status: ResponseStatus
    message: str


T = TypeVar("T")


class Success(JsonResponseModel, Generic[T]):
    status: Literal[ResponseStatus.OK] = Field(
        default=ResponseStatus.OK, title="Response Status"
    )
    message: str = Field(default="Success", title="Message for more information")
    data: list[T] = Field(default=[], title="Response Data")


class Error(JsonResponseModel):
    status: Literal[ResponseStatus.ERROR] = Field(
        default=ResponseStatus.ERROR, title="Response Status"
    )
    message: str = Field(
        default="An error occurred, see more information in 'error' field",
        title="Message for more information",
    )
    error: ErrorInfo = Field(default=..., title="Error details")

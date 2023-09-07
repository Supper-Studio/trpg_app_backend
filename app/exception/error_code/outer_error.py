from enum import Enum

from app.exception.error_code.error_model import ErrorCodeModel, ErrorType
from app.exception.error_code.module_name import ModuleName


class OuterErrorNumber(int, Enum):
    UNKNOWN_ERROR = 0
    INVALID_ARGUMENT = 1


INVALID_ARGUMENT_ERROR_CODE = ErrorCodeModel(
    error_type=ErrorType.CLIENT_ERROR,
    module_name=ModuleName.OURTER,
    error_number=OuterErrorNumber.INVALID_ARGUMENT,
)

UNKNOWN_ERROR_CODE = ErrorCodeModel(
    error_type=ErrorType.SERVER_ERROR,
    module_name=ModuleName.OURTER,
    error_number=OuterErrorNumber.UNKNOWN_ERROR,
)

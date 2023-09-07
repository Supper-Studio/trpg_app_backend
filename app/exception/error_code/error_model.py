from enum import Enum
from typing import Annotated, Any, Callable, Optional, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, GetJsonSchemaHandler, HttpUrl
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from app.exception.error_code.module_name import ModuleName


class ErrorType(str, Enum):
    SERVER_ERROR = "S"  # "Server Error"
    CLIENT_ERROR = "C"  # "Client Error"
    DATABASE_ERROR = "D"  # "Database Error"


class ErrorCodeModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    error_type: ErrorType = Field(default=ErrorType.SERVER_ERROR)
    module_name: ModuleName = Field(default=..., ge=0, le=9999)
    error_number: int = Field(default=..., ge=0, le=9999)

    @classmethod
    def from_str(cls, raw_error_code: str) -> "ErrorCodeModel":
        """通过解析错误码字符串创建 ErrorCode 实例

        Args:
            raw_error_code (str): 原始的错误码字符串

        Raises:
            ValueError: 当错误码不合法时抛出异常

        Returns:
            ErrorCode: 新的错误码对象
        """
        if len(raw_error_code) != 9:
            raise ValueError(f"Invalid error code length: {len(raw_error_code)}")

        error_type, raw_module_name, raw_error_number = (
            raw_error_code[0],
            raw_error_code[1:5],
            raw_error_code[5:],
        )

        module_name: int = int(raw_module_name)

        if module_name not in ModuleName.__members__.values():
            raise ValueError(f"Invalid module number: {module_name}")

        error_number: int = int(raw_error_number)

        return cls(
            error_type=ErrorType(error_type),
            module_name=ModuleName(module_name),
            error_number=error_number,
        )

    def __str__(self) -> str:
        return f"{self.error_type}{self.module_name:0>4}{self.error_number:0>4}"


class _ErrorCodeAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        error_code_schema: core_schema.ChainSchema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(ErrorCodeModel.from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=error_code_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ErrorCodeModel),
                    error_code_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str,
                when_used="json",
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema: JsonSchemaValue = handler(core_schema)

        all_error_types: str = "".join(ErrorType.__members__.keys())
        json_schema.update(
            type="srting",
            pattern=f"^[{all_error_types}]" + r"\d{8}$",
            examples=[
                "S00010022",
                "C00000000",
            ],
        )
        return json_schema


PydanticErrorCode: TypeAlias = (
    Annotated[ErrorCodeModel, _ErrorCodeAnnotation]
    | Annotated[str, _ErrorCodeAnnotation]
)


class ErrorInfo(BaseModel):
    code: PydanticErrorCode = Field(default=...)
    detail: Any = Field(default=...)
    help: Optional[str] = Field(default=None)
    document_url: Optional[HttpUrl] = Field(default=None)

from time import localtime, strftime, struct_time
from typing import Annotated, Any, Callable, NoReturn, Optional, TypeAlias, TypedDict

from httpx import AsyncClient, Response
from loguru import logger
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from snowflake.server.generator import EPOCH_TIMESTAMP

from app.util.settings import Settings, SettingsManager


class ServiceStats(TypedDict):
    dc: int
    worker: int
    timestamp: int
    last_timestamp: int
    sequence: int
    sequence_overload: int
    errors: int


class GUIDClient:
    _id_service_address: str = "http://localhost:8910"

    def __init__(
        self,
    ) -> NoReturn:
        raise RuntimeError("This class is not meant to be instantiated")

    @classmethod
    def set_address(cls, host: str, port: int) -> None:
        """设置 ID 服务的根路径

        Args:
            host (str): 主机地址
            port (int): 端口号
        """
        address: str = f"http://{host}:{port}"

        cls._id_service_address = address
        logger.info(f"Set ID service address to {address}")

    @classmethod
    def get_address(cls) -> str:
        """获取 ID 服务"""
        return cls._id_service_address

    @classmethod
    def set_address_by_settings(cls) -> None:
        """将 ID 服务的根路径设置为环境变量（或 .env 文件）中的值"""
        settings: Settings = SettingsManager.get_settings()
        cls.set_address(
            host=settings.id_service.host,
            port=settings.id_service.port,
        )

    @classmethod
    async def get_guid(cls) -> int:
        """异步请求 ID 服务提供新的 guid

        Returns:
            int: 新生成的 guid
        """
        async with AsyncClient(base_url=cls._id_service_address) as client:
            res: Response = await client.get("/")
            return int(res.text)

    @classmethod
    async def get_service_status(cls) -> ServiceStats:
        """异步请求 ID 服务状态信息

        Returns:
            ServiceStats: 状态信息字典
        """
        async with AsyncClient(base_url=cls._id_service_address) as client:
            res: Response = await client.get("/stats")
            return ServiceStats(res.json())


class GUIDDetail(TypedDict):
    guid: int
    timestamp: float
    time_str: str
    data_center: int
    worker: int
    sequence: int


class GUID:
    """使用雪花算法生成的全局唯一识别码，依赖于 pysnowflake 生成

    :+-------+-------------------------------------------+------------+----------+--------------+
    :|  Sign |                  Timestamp                | DataCenter |  Worker  |   Sequence   |
    :|-------+-------------------------------------------+------------+----------+--------------|
    :| 1 bit |                   41 bit                  |   2 bit    |  8 bit   |    12 bit    |
    :|-------+-------------------------------------------+------------+----------+--------------|
    :|   0b  | 10000011010101010111000101110110001000110 |     01     | 00010111 | 000000000001 |
    :+-------+-------------------------------------------+------------+----------+--------------+

    """

    _guid: int = 0
    __create_key = object()

    def __init__(self, guid: int, key: object) -> None:
        assert key == GUID.__create_key, (
            "GUID can only be created with "
            + "GUID.generate(), GUID.from_str() or GUID.from_int()"
        )

        self._guid = guid

    @classmethod
    async def generate(cls) -> "GUID":
        """从服务端获取新的 GUID

        Returns:
            GUID: 新的 GUID 对象
        """
        return cls(await GUIDClient.get_guid(), cls.__create_key)

    @classmethod
    async def from_int(cls, guid: int) -> "GUID":
        """将数字类型的 GUID 转换为 GUID 对象

        Args:
            guid (int): 数字类型的 GUID

        Returns:
            GUID: 新的 GUID 对象
        """
        if not await cls.is_valid(guid):
            raise ValueError(f"'{guid}' is not a valid GUID")

        return cls(guid, cls.__create_key)

    @classmethod
    async def from_str(cls, guid: str) -> "GUID":
        """将 GUID 字符串转换为 GUID 对象

        Args:
            guid (str): GUID 字符串

        Returns:
            GUID: 新的 GUID 对象
        """
        if not guid.isdigit():
            raise ValueError(f"guid ({guid}) is not a number")

        return await cls.from_int(int(guid))

    @property
    def guid(self) -> int:
        """获取数字类型的 GUID

        Returns:
            int: guid
        """
        return self._guid

    @property
    def create_timestamp_ms(self) -> int:
        """获取 GUID 创建时的时间戳

        Returns:
            int: 41 bit 时间戳，单位为毫秒
        """
        return (self._guid >> 22) + EPOCH_TIMESTAMP

    @property
    def create_time_str(self) -> str:
        """获取 GUID 创建时的时间字符串

        Returns:
            str: 时间字符串，格式为： YYYY-MM-DD HH:mm:ss
        """
        return self.get_custom_create_time_str()

    @property
    def data_center(self) -> int:
        """获取生成 GUID 数据中心序号

        Returns:
            int: 2 bit 的序列号
        """
        return self._guid >> 20 & 0x03  # pysnowflake 的实现中使用了 2 bit 的 dc 序列号

    @property
    def worker(self) -> int:
        """获取生成 GUID 的机器序列号

        Returns:
            int: 8 bit 的序列号
        """
        return self._guid >> 12 & 0xFF  # pysnowflake 的实现中使用了 8 位的 worker 序列号

    @property
    def sequence(self) -> int:
        """获取 GUID 的生成序列号

        Returns:
            int: 12 bit 的序列号
        """
        return self._guid & 0xFFF

    @staticmethod
    async def is_valid(guid: int) -> bool:
        """判断 GUID 是否合法，时间戳应该必须比服务器时间小

        Args:
            GUID (int): 要检查的 GUID

        Returns:
            bool: 如果合法则返回真
        """
        status: ServiceStats = await GUIDClient.get_service_status()

        guid_raw_timestamp: int = guid >> 22

        if guid_raw_timestamp <= EPOCH_TIMESTAMP:
            return False

        guid_timestamp: int = guid_raw_timestamp + EPOCH_TIMESTAMP
        current_timestamp: int = status.get("timestamp")

        return guid_timestamp <= current_timestamp

    def get_custom_create_time_str(self, format_str: Optional[str] = None) -> str:
        """获取 GUID 创建时的时间字符串

        Args:
            format_str(str): 格式字符串，默认格式为： YYYY-MM-DD HH:mm:ss. Defaults to None.

        Returns:
            str: 时间字符串
        """
        time_dict: struct_time = localtime(self.create_timestamp_ms / 1000)
        return strftime(format_str or "%Y-%m-%d %H:%M:%S", time_dict)

    def get_all_details(self) -> GUIDDetail:
        """获取 GUID 的详细信息

        Returns:
            GUIDDetail: GUID 包含的全部信息
        """
        return {
            "guid": self._guid,
            "timestamp": self.create_timestamp_ms,
            "time_str": self.create_time_str,
            "data_center": self.data_center,
            "worker": self.worker,
            "sequence": self.sequence,
        }

    def __eq__(self, other: object) -> bool:
        # sourcery skip: assign-if-exp, reintroduce-else
        if isinstance(other, GUID):
            return self._guid == other.guid

        if isinstance(other, int):
            return self._guid == other

        if isinstance(other, str):
            return str(self._guid) == other

        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        """将 GUID 转化为字符串

        用于发送给前端，因为 JS 的 Number 类型最大长度只有 53 位，并不能直接存储 64 位的 GUID 。

        Returns:
            str: 转化后的字符串
        """
        return str(self._guid)

    def __repr__(self) -> str:
        info: Generator[str, None, None] = (
            f"{k}={v}" for k, v in self.get_all_details().items()
        )
        return f"GUID({', '.join(info)})"

    # @classmethod
    # def __get_pydantic_core_schema__(
    #     cls, source_type: Any, handler: GetCoreSchemaHandler
    # ) -> CoreSchema:
    #     return core_schema.no_info_after_validator_function(cls, handler(str))


class _GUIDAnnotation:
    """用于给 Pydantic 使用的 GUID 的类型注释

    see: https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        guid_schema: core_schema.ChainSchema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(GUID),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=guid_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(GUID),
                    guid_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.guid,
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema: JsonSchemaValue = handler(core_schema)
        json_schema.update(
            type="srting",
            pattern=r"^\d{19}$",
            examples=[
                "4795229142125641729",
                "4795229255837417473",
            ],
        )
        return json_schema


PydanticGUID: TypeAlias = (
    Annotated[GUID, _GUIDAnnotation]
    | Annotated[int, _GUIDAnnotation]
    | Annotated[str, _GUIDAnnotation]
)

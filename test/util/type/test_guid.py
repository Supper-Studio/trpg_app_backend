from json import loads
from re import Match, match
from test.run_order import TestType
from time import strftime
from typing import Any, Optional

import pytest
from pydantic import BaseModel, Field, ValidationError

from app.util.settings import SettingsManager
from app.util.type.guid import GUID, GUIDClient, GUIDDetail, PydanticGUID, ServiceStats


@pytest.fixture(scope="class")
def set_id_service_address() -> None:
    """加载设置中的 ID 服务地址"""
    GUIDClient.set_address_by_settings()


@pytest.mark.unit_test
@pytest.mark.run(order=TestType.UNIT_TEST)
@pytest.mark.usefixtures("set_id_service_address")
class TestGUIDClient:
    def test_init(self) -> None:
        with pytest.raises(RuntimeError, match=r"not meant to be instantiated"):
            GUIDClient()

    def test_get_address(self) -> None:
        assert GUIDClient.get_address() == getattr(GUIDClient, "_id_service_address")

    @pytest.mark.parametrize(
        ["host", "port"],
        [
            ("localhost", 8910),
            ("127.0.0.1", 8910),
        ],
    )
    def test_set_address(self, host: str, port: int) -> None:
        GUIDClient.set_address(host, port)
        assert GUIDClient.get_address() == f"http://{host}:{port}"

    def test_set_address_by_settings(self) -> None:
        id_service = SettingsManager.get_settings().id_service

        GUIDClient.set_address_by_settings()
        assert GUIDClient.get_address() == f"http://{id_service.host}:{id_service.port}"

    def test_get_guid(self) -> None:
        guid: int = GUIDClient.get_guid()

        assert isinstance(guid, int)
        assert GUID.is_valid(guid)

    async def test_get_guid_async(self) -> None:
        guid: int = await GUIDClient.get_guid_async()

        assert isinstance(guid, int)
        assert GUID.is_valid_async(guid)

    def test_get_service_status(self) -> None:
        status: ServiceStats = GUIDClient.get_service_status()

        assert isinstance(status, dict)
        assert (
            status.keys() == ServiceStats.__required_keys__  # pylint: disable=no-member
        )

    async def test_get_service_status_async(self) -> None:
        status: ServiceStats = await GUIDClient.get_service_status_async()

        assert isinstance(status, dict)
        assert (
            status.keys() == ServiceStats.__required_keys__  # pylint: disable=no-member
        )


@pytest.fixture
def guid_instance() -> GUID:
    """创建一个新的 GUID 实例"""
    return GUID.generate()


@pytest.fixture
def client_guid() -> int:
    """从 ID 服务客户端中获取一个 GUID"""
    return GUIDClient.get_guid()


@pytest.fixture
def service_status() -> ServiceStats:
    """从 ID 服务客户端获取服务状态"""
    return GUIDClient.get_service_status()


INVALID_GUID_INTEGER: list[int] = [
    12345678901234,
    -12345678901234,
    0,
    -1,
]

INVALID_GUID_STRING: list[tuple[str, str]] = [
    ("0", r"is not a valid GUID"),
    ("0x42919b569dbffe38", r"is not a number"),
    ("abc", r"is not a number"),
]

PLUS_SECOND: list[int] = [
    1,
    10,
    1000000,
    365 * 24 * 60 * 60,
]


@pytest.mark.unit_test
@pytest.mark.run(order=TestType.UNIT_TEST)
@pytest.mark.usefixtures("set_id_service_address")
class TestGUID:
    # pylint: disable=unneeded-not

    def test_init(self, client_guid: int) -> None:
        with pytest.raises(AssertionError, match=r"GUID can only be created with"):
            GUID(client_guid, object())

    def _is_guid_instance_valid(
        self,
        guid_instance: GUID,
        from_guid: Optional[int] = None,
    ) -> None:
        assert isinstance(guid_instance, GUID)
        assert GUID.is_valid(guid_instance.guid)

        if from_guid is not None:
            assert guid_instance.guid == from_guid

    def test_generate(self) -> None:
        _guid_instance: GUID = GUID.generate()
        self._is_guid_instance_valid(_guid_instance)

    async def test_generate_async(self) -> None:
        _guid_instance: GUID = await GUID.generate_async()
        self._is_guid_instance_valid(_guid_instance)

    def test_from_int(self, client_guid: int) -> None:
        _guid_instance: GUID = GUID.from_int(client_guid)
        self._is_guid_instance_valid(_guid_instance, client_guid)

    @pytest.mark.parametrize("guid", INVALID_GUID_INTEGER)
    def test_from_int_invalid_args(self, guid: int) -> None:
        with pytest.raises(ValueError, match=r"is not a valid GUID"):
            GUID.from_int(guid)

    async def test_from_int_async(self, client_guid: int) -> None:
        _guid_instance: GUID = await GUID.from_int_async(client_guid)
        self._is_guid_instance_valid(_guid_instance, client_guid)

    @pytest.mark.parametrize("guid", INVALID_GUID_INTEGER)
    async def test_from_int_async_invalid_args(self, guid: int) -> None:
        with pytest.raises(ValueError, match=r"is not a valid GUID"):
            await GUID.from_int_async(guid)

    def test_from_str(self, client_guid: int) -> None:
        _guid_instance: GUID = GUID.from_str(str(client_guid))
        self._is_guid_instance_valid(_guid_instance, client_guid)

    @pytest.mark.parametrize(["guid", "error_pattern"], INVALID_GUID_STRING)
    def test_from_str_invalid_args(self, guid: int, error_pattern) -> None:
        with pytest.raises(ValueError, match=error_pattern):
            GUID.from_str(str(guid))

    async def test_from_str_async(self, client_guid: int) -> None:
        _guid_instance: GUID = await GUID.from_str_async(str(client_guid))
        self._is_guid_instance_valid(_guid_instance, client_guid)

    @pytest.mark.parametrize(["guid", "error_pattern"], INVALID_GUID_STRING)
    async def test_from_str_async_invalid_args(
        self, guid: str, error_pattern: str
    ) -> None:
        with pytest.raises(ValueError, match=error_pattern):
            await GUID.from_str_async(guid)

    def test_guid(self, client_guid: int) -> None:
        _guid_instance: GUID = GUID.from_int(client_guid)
        assert _guid_instance.guid == client_guid

    @pytest.mark.parametrize(
        ["instance_property", "stats_property"],
        [
            ("create_timestamp_ms", "last_timestamp"),
            ("data_center", "dc"),
            ("worker", "worker"),
            ("sequence", "sequence"),
        ],
    )
    def test_guid_info_property(
        self,
        guid_instance: GUID,
        service_status: ServiceStats,
        instance_property: str,
        stats_property: str,
    ) -> None:
        attr_from_instance = getattr(guid_instance, instance_property)
        attr_from_service = service_status[stats_property]
        assert attr_from_instance == attr_from_service

    def test_create_time_str(self, guid_instance: GUID) -> None:
        assert (
            guid_instance.get_custom_create_time_str() == guid_instance.create_time_str
        )

    def test_is_valid(self, client_guid: int) -> None:
        assert GUID.is_valid(client_guid)

    async def test_is_valid_async(self, client_guid: int) -> None:
        assert await GUID.is_valid_async(client_guid)

    @pytest.mark.parametrize("guid", INVALID_GUID_INTEGER)
    def test_is_valid_invalid_args(self, guid: int) -> None:
        assert not GUID.is_valid(guid)

    @pytest.mark.parametrize("guid", INVALID_GUID_INTEGER)
    async def test_is_valid_async_invalid_args(self, guid: int) -> None:
        assert not await GUID.is_valid_async(guid)

    @pytest.mark.parametrize("plus_second", PLUS_SECOND)
    def test_is_valid_future_timestamp(
        self, client_guid: int, plus_second: int
    ) -> None:
        assert not GUID.is_valid(client_guid + ((plus_second * 1000) << 22))

    @pytest.mark.parametrize("plus_second", PLUS_SECOND)
    async def test_is_valid_async_future_timestamp(
        self, client_guid: int, plus_second: int
    ) -> None:
        assert not await GUID.is_valid_async(client_guid + ((plus_second * 1000) << 22))

    def test_get_custom_create_time_str(self, guid_instance: GUID) -> None:
        time_str_format: str = r"%Y-%m-%d %H:%M:%S"
        time_str: str = guid_instance.get_custom_create_time_str(time_str_format)

        result: Match[str] | None = match(
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", time_str
        )

        assert result is not None
        assert result.group() == strftime(time_str_format)

    @pytest.mark.parametrize(
        ["detail_key", "property_name"],
        [
            ("guid", "guid"),
            ("timestamp", "create_timestamp_ms"),
            ("time_str", "create_time_str"),
            ("data_center", "data_center"),
            ("worker", "worker"),
            ("sequence", "sequence"),
        ],
    )
    def test_get_all_details(
        self, guid_instance: GUID, detail_key: str, property_name: str
    ) -> None:
        detail: GUIDDetail = guid_instance.get_all_details()

        assert isinstance(detail, dict)
        assert detail_key in detail.keys()
        assert detail[detail_key] == getattr(guid_instance, property_name)

    @pytest.mark.parametrize(
        "other_type",
        [
            int,
            str,
        ],
    )
    def test_eq(self, client_guid: int, other_type: type[Any]) -> None:
        assert GUID.from_int(client_guid) == other_type(client_guid)

    def test_eq_self(self, guid_instance: GUID) -> None:
        assert guid_instance == guid_instance

    @pytest.mark.parametrize(
        "other_type",
        [
            float,
        ],
    )
    def test_eq_invalid_args(self, client_guid: int, other_type: type[Any]) -> None:
        assert GUID.from_int(client_guid) != other_type(client_guid)

    def test_str(self, client_guid: int) -> None:
        assert str(GUID.from_int(client_guid)) == str(client_guid)

    def test_repr(self, guid_instance: GUID) -> None:
        assert f"GUID({guid_instance.guid})" == repr(guid_instance)


class SomeModel(BaseModel):
    id: PydanticGUID


class SomeModelWithDefaults(BaseModel):
    id: PydanticGUID = Field(default_factory=GUID.generate)


@pytest.mark.smoke_test
@pytest.mark.run(order=TestType.SMOKE_TEST)
class TestPydanticGUID:
    def _is_model_instance_valid(
        self,
        _model_instance: SomeModel | SomeModelWithDefaults,
        from_guid: Optional[int] = None,
    ) -> None:
        assert isinstance(_model_instance.id, GUID)

        if from_guid is not None:
            assert _model_instance.id.guid == from_guid

    def test_guid_in_model_from_int(self, client_guid: int) -> None:
        _model_instance = SomeModel(id=client_guid)
        self._is_model_instance_valid(_model_instance, client_guid)

    def test_guid_in_model_from_str(self, client_guid: int) -> None:
        _model_instance = SomeModel(id=str(client_guid))
        self._is_model_instance_valid(_model_instance, client_guid)

    def test_guid_in_model_from_guid(self, guid_instance: GUID) -> None:
        _model_instance = SomeModel(id=guid_instance)
        self._is_model_instance_valid(_model_instance, guid_instance.guid)

    def test_guid_in_model_from_default_factory(self) -> None:
        _model_instance = SomeModelWithDefaults()
        self._is_model_instance_valid(_model_instance)

    @pytest.mark.parametrize("guid", INVALID_GUID_INTEGER)
    def test_guid_in_model_invalid_args(self, guid: int) -> None:
        with pytest.raises(ValueError, match=r"is not a valid GUID"):
            SomeModel(id=guid)

    @pytest.mark.parametrize(["guid", "_"], INVALID_GUID_STRING)
    def test_guid_in_model_invalid_strings(self, guid: str, _: str) -> None:
        with pytest.raises(ValidationError):
            SomeModel(id=guid)

    def test_guid_in_model_dump(self, client_guid: int) -> None:
        some_model: SomeModel = SomeModel(id=client_guid)

        assert some_model.model_dump() == {
            "id": client_guid,
        }

        assert loads(some_model.model_dump_json()) == {
            "id": str(client_guid),
        }

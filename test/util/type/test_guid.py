from re import Match, match
from time import strftime

import pytest
from pydantic import BaseModel, Field
from snowflake import client

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

    @pytest.mark.asyncio
    async def test_get_guid(self) -> None:
        guid: int = await GUIDClient.get_guid()

        assert isinstance(guid, int)
        assert GUID.is_valid(guid)

    @pytest.mark.asyncio
    async def test_get_service_status(self) -> None:
        status: ServiceStats = await GUIDClient.get_service_status()

        assert isinstance(status, dict)
        assert (
            status.keys() == ServiceStats.__required_keys__  # pylint: disable=no-member
        )



@pytest.fixture(scope="session")
def snowflake_client() -> None:
    """初始化一个 Snowflake ID 服务的客户端"""
    client.setup("localhost", "8910")


@pytest.fixture
def new_client_guid() -> int:
    """从 Snowflake ID 服务中获取一个新的 GUID

    Returns:
        int: 获取到的新的 GUID
    """
    return client.get_guid()


@pytest.fixture
def new_guid() -> GUID:
    """创建一个新的 GUID 对象

    Returns:
        GUID: 新构造的 GUID 实例
    """
    return GUID(client.get_guid())


@pytest.mark.usefixtures("snowflake_client")
class TestGUID:
    # pylint: disable=unneeded-not
    def test_init(self, new_client_guid: int) -> None:
        guid = GUID(new_client_guid)
        assert isinstance(guid, GUID)

        guid = GUID(new_client_guid, need_validate=False)
        assert isinstance(guid, GUID)

        with pytest.raises(ValueError, match=r".* is not a valid GUID"):
            GUID(123)

    def test_parse_str(self, new_client_guid: int) -> None:
        with pytest.raises(ValueError, match=r"guid .* is not a number"):
            GUID.parse_str("abc")

        with pytest.raises(ValueError, match=r".* is not a valid GUID"):
            GUID(123)

        guid: GUID = GUID.parse_str(str(new_client_guid))
        assert isinstance(guid, GUID)

    def test_guid(self, new_client_guid: int) -> None:
        guid: GUID = GUID(new_client_guid)
        assert guid.guid == new_client_guid

    def test_create_timestamp_ms(self, new_guid: GUID) -> None:
        assert new_guid.create_timestamp_ms == client.get_stats().get("last_timestamp")

    def test_create_time_str(self, new_guid: GUID) -> None:
        assert new_guid.get_custom_create_time_str() == new_guid.create_time_str

    def test_center(self, new_guid: GUID) -> None:
        assert new_guid.data_center == client.get_stats().get("dc")

    def test_worker(self, new_guid: GUID) -> None:
        assert new_guid.worker == client.get_stats().get("worker")

    def test_equence(self, new_guid: GUID) -> None:
        assert new_guid.sequence == client.get_stats().get("sequence")

    def test_is_valid(self, new_client_guid: int) -> None:
        assert not GUID.is_valid(0)
        assert not GUID.is_valid(-1)
        assert GUID.is_valid(new_client_guid)
        assert GUID.is_valid(GUID.generate().guid)
        assert not GUID.is_valid(client.get_guid() + (1000 << 22))

    def test_get_custom_create_time_str(self, new_guid: GUID) -> None:
        time_str_format: str = r"%Y-%m-%d %H:%M:%S"
        time_str: str = new_guid.get_custom_create_time_str(time_str_format)

        result: Match[str] | None = match(
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", time_str
        )

        assert result is not None
        assert result.group() == strftime(time_str_format)

    def test_get_all_details(self, new_guid: GUID) -> None:
        details: GUIDDetail = new_guid.get_all_details()

        assert isinstance(details, dict)
        assert list(details.keys()) == [
            "guid",
            "timestamp",
            "time_str",
            "data_center",
            "worker",
            "sequence",
        ]

        assert details["guid"] == new_guid.guid
        assert details["timestamp"] == new_guid.create_timestamp_ms
        assert details["time_str"] == new_guid.create_time_str
        assert details["data_center"] == new_guid.data_center
        assert details["worker"] == new_guid.worker
        assert details["sequence"] == new_guid.sequence

    def test_eq(self, new_client_guid: int) -> None:  # sourcery skip: de-morgan
        guid = GUID(new_client_guid)

        assert guid == guid  # self
        assert guid == new_client_guid  # int
        assert guid == str(new_client_guid)  # str
        assert guid == GUID(new_client_guid)  # GUID

        assert not guid == float(new_client_guid)

    def test_ne(self, new_client_guid: int) -> None:  # sourcery skip: de-morgan
        guid = GUID(new_client_guid)

        assert not guid != guid  # self
        assert not guid != new_client_guid  # int
        assert not guid != str(new_client_guid)  # str
        assert not guid != GUID(new_client_guid)  # GUID

        assert guid != float(new_client_guid)

    def test_str(self, new_client_guid: int) -> None:
        guid: GUID = GUID(new_client_guid)
        assert str(guid) == str(new_client_guid)

    def test_repr(self, new_guid: GUID) -> None:
        repr_info: list[str] = [
            f"{k}={v}" for k, v in new_guid.get_all_details().items()
        ]

        assert f"GUID({', '.join(repr_info)})" == repr(new_guid)


def test_guid_in_model(new_client_guid: int) -> None:
    class SomeModel(BaseModel):
        id: PydanticGUID
        name: str

    some_model: SomeModel = SomeModel(
        id=str(new_client_guid),
        name="test",
    )

    assert isinstance(some_model.id, GUID)
    assert some_model.id.guid == new_client_guid

    some_model = SomeModel(
        id=GUID(new_client_guid),
        name="123",
    )

    assert isinstance(some_model.id, GUID)
    assert some_model.id.guid == new_client_guid

    some_model = SomeModel(
        id=new_client_guid,
        name="123",
    )

    assert isinstance(some_model.id, GUID)
    assert some_model.id.guid == new_client_guid

    with pytest.raises(ValueError, match=r".* is not a valid GUID"):
        SomeModel(
            id=123,
            name="123",
        )


def test_guid_in_field_default_factory() -> None:
    class SomeModel(BaseModel):
        id: PydanticGUID = Field(default_factory=GUID)
        name: str

    some_model: SomeModel = SomeModel(
        name="test",
    )

    assert isinstance(some_model.id, GUID)

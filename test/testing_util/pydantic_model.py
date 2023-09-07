from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, TypeAlias, TypedDict

import pytest
from pydantic import BaseModel, ValidationError


class CheckType(int, Enum):
    ALL = 0
    NONE = 1
    INCLUDE = 2
    EXCLUDE = 3


FieldKeys: TypeAlias = Iterable[str]


class FieldMarker(TypedDict):
    fields: FieldKeys
    type: CheckType


class PydanticModel(ABC):
    @pytest.fixture
    @abstractmethod
    def _model_instance(self) -> BaseModel:
        ...

    __frozen_field__: FieldMarker = {
        "fields": [],
        "type": CheckType.INCLUDE,
    }

    @pytest.fixture
    def _need_checked_fields(self, request: pytest.FixtureRequest) -> FieldKeys:
        field_marker: FieldMarker = request.param
        _model_instance: BaseModel = request.getfixturevalue("_model_instance")

        marker_type: CheckType = field_marker["type"]
        marked_fields: Iterable[str] = field_marker["fields"]

        if marker_type == CheckType.NONE:
            return []

        all_field_keys = _model_instance.model_fields.keys()

        if marker_type == CheckType.ALL:
            return all_field_keys

        if marker_type == CheckType.INCLUDE:
            return [i for i in all_field_keys if i in marked_fields]

        if marker_type == CheckType.EXCLUDE:
            return [i for i in all_field_keys if i not in marked_fields]

        raise ValueError(f"Unknown check type: {marker_type}")

    @pytest.mark.parametrize("_need_checked_fields", [__frozen_field__], indirect=True)
    def test_frozen_fields(
        self,
        _model_instance: BaseModel,
        _need_checked_fields: FieldKeys,
    ) -> None:
        for field in _need_checked_fields:
            with pytest.raises(ValidationError, match=r"is frozen"):
                setattr(_model_instance, field, getattr(_model_instance, field))


class PydanticFrozenModel(PydanticModel, ABC):
    @pytest.fixture
    @abstractmethod
    def _model_instance(self) -> BaseModel:
        ...

    __frozen_field__: FieldMarker = {
        "fields": [],
        "type": CheckType.ALL,
    }

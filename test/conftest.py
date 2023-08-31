from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

import pytest


@pytest.fixture
def not_existing_file() -> Path:
    """创建一个并不存在的文件路径用于测试

    Returns:
        Path: 用于测试的路径
    """
    return Path("not_existing_file.txt")


@pytest.fixture
def not_existing_directory() -> Path:
    """创建一个并不存在的路径用于测试

    Returns:
        Path: 测试用的路径
    """
    return Path("not_existing_directory")


@pytest.fixture
def temp_file() -> Iterable[Path]:
    """创建一个临时文件用于测试

    Yields:
        Iterator[Iterable[Path]]: 测试用的真实存在的临时文件
    """
    with NamedTemporaryFile(mode="r") as temp_file:
        yield Path(temp_file.name)

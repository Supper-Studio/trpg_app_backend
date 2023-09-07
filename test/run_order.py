from enum import IntEnum

import pytest


@pytest.mark.skip
class TestType(IntEnum):
    """用于给测试样例排序，主要用在给 @pytest.mark.run 装饰器中的 order 参数传值

    Example:
        @pytest.mark.run(order=TestType.INTEGRATION_TEST)
        def test_integration_test():
            pass
    """

    UNIT_TEST = 1
    SMOKE_TEST = 2
    INTEGRATION_TEST = 3

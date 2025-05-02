import asyncio

from debounce.aio import debounce

import pytest


@pytest.mark.asyncio
async def test_bounce_function():
    """Test that normal functions can be debounced."""
    @debounce(0.1)
    async def bouncy(obj_):
        obj_["test"] = 1

    obj = {}
    await bouncy(obj)
    assert "test" not in obj
    await asyncio.sleep(0.2)
    assert obj["test"] == 1


@pytest.mark.asyncio
async def test_calling_function_gives_only_last_value():
    @debounce(0.3)
    async def bouncy_1(obj_, value):
        obj_["test"] = value

    obj = {}
    await bouncy_1(obj, 3)
    await bouncy_1(obj, 4)
    assert "test" not in obj
    await asyncio.sleep(0.4)
    assert obj["test"] == 4


@pytest.mark.asyncio
async def test_different_functions_can_be_debounced(bounced):
    @debounce(0.3)
    async def bouncy_1(obj_, value):
        obj_["test"] = value

    @debounce(0.1)
    async def bouncy_2(obj_, value):
        obj_["test2"] = value

    obj = {}
    await bouncy_1(obj, 3)
    await bouncy_2(obj, 4)
    await bouncy_1(obj, 4)
    await asyncio.sleep(0.2)
    # First debounce is on 0.1 and the second on 0.3
    # waiting 0.2 should set the first timer but not the second.
    assert "test" not in obj
    assert obj["test2"] == 4
    await asyncio.sleep(0.2)
    assert obj["test"] == 4


@pytest.mark.asyncio
async def test_repeated_bounce_delays(bounced):
    """Repeatedly calling a debounced function will reset it.

    It will only be called after a long enough time.
    """

    @debounce(0.3)
    async def bouncy_1(obj_, value):
        obj_["test"] = value

    obj = {}
    for i in range(10):
        await bouncy_1(obj, 3)
        await asyncio.sleep(0.1)
        if "test" in obj:
            assert False

    await asyncio.sleep(0.5)
    assert obj["test"] == 3


@pytest.mark.asyncio
async def test_cancel_bounce(bounced):
    @debounce(0.3)
    async def bouncy_1(obj_, value):
        obj_["test"] = value

    obj = {}
    await bouncy_1(obj, 3)
    bouncy_1.cancel()
    assert "test" not in obj
    await asyncio.sleep(0.5)
    assert "test" not in obj


@pytest.mark.asyncio
async def test_flush_bounce(bounced):
    @debounce(0.3)
    async def bouncy_1(obj_, value):
        obj_["test"] = value

    obj = {}
    await bouncy_1(obj, 3)
    await bouncy_1.flush()
    assert obj["test"] == 3

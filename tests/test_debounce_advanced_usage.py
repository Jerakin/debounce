from time import sleep

from debounce import debounce

def test_cancel_bounce(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_1.cancel()
    sleep(0.4)
    assert bounced.value_1 == 0


def test_cancel_bounce_doesnt_cancel_other(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_2(4)
    bounced.debounced_function_1.cancel()
    sleep(0.4)
    assert bounced.value_2 == 4
    assert bounced.value_1 == 0

def test_cancel_no_initial_call(bounced):
    """Cancel a not-yet-called bounced function does nothing."""
    bounced.debounced_function_1.cancel()
    sleep(0.4)
    assert bounced.value_1 == 0


def test_flush_bounce(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_1.flush()
    assert bounced.value_1 == 3
    sleep(0.4)
    assert bounced.value_1 == 3


def test_flush_bounce_no_initial_call(bounced):
    """Cancel a not-yet-called bounced function does nothing."""
    bounced.debounced_function_1.flush()
    assert bounced.value_1 == 0
    sleep(0.4)
    assert bounced.value_1 == 0


def test_flush_after_cancel(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_1.cancel()
    bounced.debounced_function_1.flush()
    assert bounced.value_1 == 3


def test_flush_bounce_doesnt_flush_other(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_2(4)
    bounced.debounced_function_1.flush()
    assert bounced.value_1 == 3
    assert bounced.value_2 == 0
    sleep(0.4)
    assert bounced.value_2 == 4
    assert bounced.value_1 == 3


def test_bounce_leading(bounced):
    assert bounced.value_leading == 0
    bounced.debounced_function_leading(3)
    assert bounced.value_leading == 3
    bounced.debounced_function_leading(2)
    sleep(1)
    assert bounced.value_leading == 2
    assert bounced.debounced_function_leading.info()["calls"] == 2


def test_bounce_leading_repeat(bounced):
    @debounce(0.2, leading=True)
    def bouncy(obj_):
        obj_["test"] += 1

    obj = {"test": 0}

    # Our first call is immediate
    bouncy(obj)
    assert obj["test"] == 1

    for _ in range(10):
        bouncy(obj)
        sleep(0.1)
    # The looped calls are too fast to change anything
    assert obj["test"] == 1

    # After a wait the last call comes through
    sleep(0.3)
    assert bouncy.info()["calls"] == 2
    assert obj["test"] == 2


def test_bounce_leading_calls_only_once_if_no_repeated_calls(bounced):
    @debounce(0.2, leading=True)
    def bouncy(obj_):
        obj_["test"] += 1

    obj = {"test": 0}
    assert obj["test"] == 0
    bouncy(obj)
    assert obj["test"] == 1
    sleep(0.3)
    assert bouncy.info()["calls"] == 1
    assert obj["test"] == 1


def test_max_wait_will_eventually_call(bounced):
    while True:
        bounced.debounced_function_max_time(3)
        sleep(0.1)
        if bounced.value_max_time == 3:
            break
    assert True


def test_repeated_bounce_stalls_forever(bounced):
    """Repeated calls will never set the value.

    Simulate that by calling it 100 times.
    """
    calls = 0
    while True:
        calls += 1
        bounced.debounced_function_1(3)
        sleep(0.1)
        if bounced.value_1 == 3:
            assert False
        if calls >= 100:
            break
    assert True


def test_max_wait_resets_timer(bounced):
    while True:
        bounced.debounced_function_max_time(3)
        sleep(0.1)
        if bounced.value_max_time == 3:
            break
    assert bounced.value_max_time == 3

    bounced.debounced_function_max_time(2)
    sleep(0.1)
    assert bounced.value_max_time == 3

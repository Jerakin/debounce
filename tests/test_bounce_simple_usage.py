from time import sleep

from debounce import debounce

import pytest

def test_bounce_function():
    """Test that normal functions can be debounced."""
    @debounce(0.5)
    def bouncy(obj_):
        obj_["test"] = 1

    obj = {}
    bouncy(obj)
    assert "test" not in obj
    sleep(0.6)
    assert obj["test"] == 1



def test_calling_no_args_function(bounced):
    """Calling debounce without arguments isn't supported."""
    with pytest.raises(TypeError):
        @debounce
        def bouncy():
            pass

def test_calling_function_gives_value_after_time(bounced, function_1_call_time):
    bounced.debounced_function_1(3)
    assert bounced.value_1 == 0
    sleep(function_1_call_time)
    assert bounced.value_1 == 3


def test_calling_function_gives_only_last_value(bounced, function_1_call_time):
    bounced.debounced_function_1(3)
    bounced.debounced_function_1(4)
    assert bounced.value_1 == 0
    sleep(function_1_call_time)
    assert bounced.value_1 == 4


def test_different_functions_can_be_debounced(bounced):
    bounced.debounced_function_1(3)
    bounced.debounced_function_2(4)
    bounced.debounced_function_1(4)
    sleep(0.2)
    # First debounce is on 0.1 and the second on 0.3
    # waiting 0.2 should set the first timer but not the second.
    assert bounced.value_1 == 0
    assert bounced.value_2 == 4
    sleep(0.2)
    assert bounced.value_1 == 4


def test_repeated_bounce_delays(bounced):
    """Repeatedly calling a debounced function will reset it.

    It will only be called after a long enough time.
    """
    for i in range(10):
        bounced.debounced_function_1(3)
        sleep(0.1)
        if bounced.value_1 == 3:
            assert False

    sleep(0.5)
    assert bounced.value_1 == 3

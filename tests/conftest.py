import pytest

from debounce import debounce

class Bounced:
    def __init__(self):
        self.value_1 = 0
        self.value_2 = 0
        self.value_increment = 0
        self.value_no_args = 0
        self.value_leading = 0
        self.value_max_time = 0
        self.value_sleepy = 0

    @debounce(0.3)
    def debounced_function_1(self, value):
        self.value_1 = value

    @debounce(0.1)
    def debounced_function_2(self, value):
        self.value_2 = value

    @debounce(0.2, leading=True)
    def debounced_function_increment(self):
        self.value_increment += 1

    @debounce(0.3)
    def debounced_function_no_args(self):
        self.value_no_args = 1

    @debounce(0.3, leading=True)
    def debounced_function_leading(self, value):
        self.value_leading = value

    @debounce(0.3, max_wait=1)
    def debounced_function_max_time(self, value):
        self.value_max_time = value


@pytest.fixture
def function_1_call_time():
    return 0.3 + 0.5


@pytest.fixture
def function_2_call_time():
    return 0.1 + 0.5


@pytest.fixture(scope="function")
def bounced():
    return Bounced()

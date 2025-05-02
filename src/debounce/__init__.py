from __future__ import annotations

import threading
import time
from functools import partial, partialmethod
from typing import TYPE_CHECKING, Callable
import inspect

from debounce.aio import _debounce_wrapper_async


if TYPE_CHECKING:
    from typing import Callable, Coroutine, Any

    class _TypeDebounceCallable(Callable):
        def __call__(self, *args, **kwargs) -> Callable[..., None] | Coroutine[Any, Any, None]: ...
        def flush(self) -> None:
            """Immediately call the debounced function."""
        def cancel(self) -> None:
            """Cancel the debounced function."""
        def info(self) -> dict:
            """Return a dictionary of calls and skips."""


def debounce(
        wait: float,
        *,
        leading: bool = False,
        max_wait: float | None = None,
) -> Callable[..., _TypeDebounceCallable]:
    """Decorator to mark a function to debounce.

    Debounced function delays invoking the function until after `wait` seconds have
     elapsed since the last time the debounced function was invoked. The debounced
     function comes with a `cancel` method to cancel delayed function invocations
     and a `flush` method to immediately invoke them.

    You can use ``@debounce(seconds, leading=True)`` to invoke the function
    once immediately, it will then work as normal.

    You can use ``@debounce(seconds, max_wait=0.5)`` to ensure the debounced
     function is called at least `max_wait` seconds apart.
    """
    if not isinstance(wait, float):
        msg = ("First argument must be a float. "
               "Ensure you call it as `@debounce(float)`.")
        raise TypeError(msg)

    def decorating_function(user_function: Callable[..., None] | Coroutine[Any, Any, None]) -> _TypeDebounceCallable[..., None]:
        if inspect.iscoroutinefunction(user_function):
            return _debounce_wrapper_async(
                user_function,
                wait,
                leading=leading,
                max_wait=max_wait,
            )
        return _debounce_wrapper(
            user_function,
            wait,
            leading=leading,
            max_wait=max_wait,
        )

    return decorating_function

def _debounce_wrapper(  # noqa: C901
        user_function: Callable[..., None],
        wait: float,
        *,
        leading: bool,
        max_wait: float,
) -> _TypeDebounceCallable:

    timer: threading.Timer | None = None
    _args = None
    _kwargs = None
    leading_called = False
    max_wait_timer = None
    calls = skips = 0
    def wrapper(*args: tuple, **kwargs: dict) -> None:
        nonlocal timer, leading_called, _args, _kwargs, max_wait_timer, skips
        _args = args
        _kwargs = kwargs

        # max wait timer start
        if max_wait and max_wait_timer is None:
            max_wait_timer = time.time()

        # If we have a max wait, and we have reached it call the users function.
        if max_wait and (time.time() - max_wait_timer) > max_wait:
            call_function(*args, **kwargs)
            return

        # If we want to call function leading but haven't already do so.
        if leading and not leading_called:
            leading_called = True
            call_function(*_args, **_kwargs)
            return

        # Cancel the timer on subsequent calls
        if timer is not None:
            skips += 1
            timer.cancel()

        timer = threading.Timer(wait, partial(call_function, *args, **kwargs))
        timer.start()

    def call_function(*args: tuple, **kwargs: dict) -> None:
        nonlocal timer, max_wait_timer, calls
        calls += 1
        max_wait_timer = None
        timer = None
        user_function(*args, **kwargs)

    def cancel() -> None:
        """Cancel the debounced function."""
        nonlocal timer, max_wait_timer
        max_wait_timer = None
        if timer is not None:
            timer.cancel()

    def flush() -> None:
        """Immediately call the debounced function."""
        nonlocal timer
        if timer is None:
            # Do not call the function if there is no timer.
            # No timer means that there is no initial call.
            return
        args = _args if _args is not None else ()
        kwargs = _kwargs if _kwargs is not None else {}

        # Cancel the timer and call the function.
        timer.cancel()
        user_function(*args, **kwargs)

    def info():
        """Return a dictionary of calls and skips."""
        nonlocal skips, calls
        return {"skips": skips, "calls": calls}

    wrapper.cancel = cancel
    wrapper.flush = flush
    wrapper.info = info
    return wrapper

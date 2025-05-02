from __future__ import annotations

import asyncio
import threading
import time
from typing import TYPE_CHECKING, Callable


if TYPE_CHECKING:
    from typing import Callable, Coroutine, Any

    class _TypeDebounceCallable(Callable):
        def __call__(self, *args, **kwargs) -> Coroutine[Any, Any, None]: ...
        def flush(self) -> None:
            """Immediately call the debounced function."""
        def cancel(self) -> None:
            """Cancel the debounced function."""


__all__ = ["debounce"]


def debounce(
        wait: float,
        *,
        leading: bool = False,
        max_wait: float | None = None,
) -> Callable[..., _TypeDebounceCallable]:
    """Asynchronous debounce decorator."""
    if not isinstance(wait, float):
        msg = ("First argument must be a float. "
               "Ensure you call it as `@debounce(float)`.")
        raise TypeError(msg)

    def decorating_function(user_function: Coroutine) -> _TypeDebounceCallable[..., None]:
        return _debounce_wrapper_async(
            user_function,
            wait,
            leading=leading,
            max_wait=max_wait,
        )
    return decorating_function


class Timer:
    def __init__(self, timeout, callback, *args, **kwargs):
        self._timeout = timeout
        self._callback = callback
        self._args = args
        self._kwargs = kwargs
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback(*self._args, **self._kwargs)

    def cancel(self):
        self._task.cancel()


def _debounce_wrapper_async(  # noqa: C901
        user_function: Coroutine,
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

    async def wrapper(*args: tuple, **kwargs: dict) -> None:
        nonlocal timer, leading_called, _args, _kwargs, max_wait_timer, skips
        _args = args
        _kwargs = kwargs

        # max wait timer start
        if max_wait and max_wait_timer is None:
            max_wait_timer = time.time()

        # If we have a max wait, and we have reached it call the users function.
        if max_wait and (time.time() - max_wait_timer) > max_wait:
            await call_function(*args, **kwargs)
            return

        # If we want to call function leading but haven't already do so.
        if leading and not leading_called:
            leading_called = True
            await call_function(*_args, **_kwargs)
            return

        # Cancel the timer on subsequent calls
        if timer is not None:
            skips += 1
            timer.cancel()

        timer = Timer(wait, call_function, *args, **kwargs)

    async def call_function(*args: tuple, **kwargs: dict) -> None:
        nonlocal timer, max_wait_timer, calls
        calls += 1
        max_wait_timer = None
        timer = None
        await user_function(*args, **kwargs)

    def cancel() -> None:
        """Cancel the debounced function."""
        nonlocal timer, max_wait_timer
        max_wait_timer = None
        if timer is not None:
            timer.cancel()

    async def flush() -> None:
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
        await call_function(*args, **kwargs)

    def info():
        """Return a dictionary of calls and skips."""
        nonlocal skips, calls
        return {"skips": skips, "calls": calls}

    wrapper.cancel = cancel
    wrapper.flush = flush
    wrapper.info = info
    return wrapper

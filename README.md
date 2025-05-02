# debounce

Debounced function delays invoking the function until after `wait` seconds have
 elapsed since the last time the debounced function was invoked. The debounced
 function comes with a `cancel` method to cancel delayed function invocations
 and a `flush` method to immediately invoke them.

**Additional arguments**

* `leading=True` - If you want it to call your function immediately on invocation.
* `max_wait=x` - The maximum time the decorated function is allowed to be delayed before it's invoked.


## Usage

```python
from debounce import debounce

@debounce(0.1)
def handle_event(e):
    """Computationally heavy methods that potentially gets polled a lot."""

```

### Cancel
```python
from debounce import debounce

@debounce(0.1)
def handle_event(e):
    """Computationally heavy methods that potentially gets polled a lot."""


# Imagine that the event has been called
handle_event(...)

# You can then cancel it by calling. The function will now never be called.
handle_event.cancel()
```

### Flush
```python
from debounce import debounce

@debounce(0.1)
def handle_event(e):
    """Computationally heavy methods that potentially gets polled a lot."""


# Imagine that the event has been called
handle_event(...)

# You can flush the call to immediately call it. 
handle_event.flush()
```


## Asyncio
It also handles `async` functions.
```python
from debounce import debounce

@debounce(0.1)
async def event(e):
    """Computationally heavy methods that potentially gets polled a lot."""
```

import threading
from collections.abc import Callable, Hashable
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


def get_or_create(
    cache: dict[K, T],
    lock: threading.Lock,
    key: K,
    build: Callable[[], T],
) -> T:
    """Return the cached instance for `key`, building it at most once.

    The factories run inside the request threadpool, so a plain
    "check, then build, then store" lets two threads build two instances and
    hand out the one that loses the race. For a memory provider that means a
    conversation written to one instance is invisible through the other, so the
    build is guarded and re-checked inside the lock.
    """
    instance = cache.get(key)

    if instance is not None:
        return instance

    with lock:
        if key not in cache:
            cache[key] = build()

        return cache[key]

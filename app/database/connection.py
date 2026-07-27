import atexit
import threading
from collections.abc import Iterator
from contextlib import contextmanager

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings
from app.core.instances import get_or_create

#: One pool per connection string. Built on first use, never at import time, so
#: importing a store does not require a running database.
_POOLS: dict[str, ConnectionPool] = {}
_POOLS_LOCK = threading.Lock()


def _build_pool(dsn: str) -> ConnectionPool:
    return ConnectionPool(
        dsn,
        min_size=settings.database_pool_min,
        max_size=settings.database_pool_max,
        kwargs={"row_factory": dict_row, "autocommit": True},
        open=True,
    )


def pool() -> ConnectionPool:
    """Return the shared connection pool of the platform database."""
    dsn = settings.database_dsn

    return get_or_create(_POOLS, _POOLS_LOCK, dsn, lambda: _build_pool(dsn))


@contextmanager
def connection() -> Iterator[Connection]:
    """Yield a pooled connection with dictionary rows and autocommit."""
    with pool().connection() as pooled:
        yield pooled


def reset_pools() -> None:
    """Close every pool.

    Registered to run at exit, because a pool keeps worker threads alive and
    a short lived script would otherwise complain on the way out.
    """
    with _POOLS_LOCK:
        for open_pool in _POOLS.values():
            open_pool.close()

        _POOLS.clear()


atexit.register(reset_pools)

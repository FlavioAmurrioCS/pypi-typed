from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from _typeshed import Incomplete


class Lazy:
    @cached_property
    def json_loads(self) -> Callable[[str], Incomplete]:
        try:
            from orjson import loads as json_loads

        except ModuleNotFoundError:
            from json import loads as json_loads

        return json_loads


lazy = Lazy()

if __name__ == "__main__":
    lazy.json_loads("")

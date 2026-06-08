from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypedDict

from typing_extensions import NotRequired
from typing_extensions import Protocol
from typing_extensions import Unpack

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


class Arguments(TypedDict):
    method: str
    url: str
    headers: NotRequired[Mapping[str, str]]
    timeout: NotRequired[float | None]


class RequestResponse(Protocol):
    @property
    def text(self) -> str: ...

    def raise_for_status(self) -> Any: ...  # noqa: ANN401


class SyncHttpRequest(Protocol):
    def __call__(self, **kwargs: Unpack[Arguments]) -> RequestResponse: ...


class AsyncHttpRequest(Protocol):
    async def __call__(self, **kwargs: Unpack[Arguments]) -> RequestResponse: ...

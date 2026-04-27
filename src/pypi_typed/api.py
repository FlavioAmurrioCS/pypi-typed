from __future__ import annotations

import json
from dataclasses import dataclass
from inspect import isawaitable
from typing import TYPE_CHECKING
from typing import Generic
from typing import Literal
from typing import TypeVar
from typing import overload

from pypi_typed._index import html_to_distribution
from pypi_typed._index import html_to_listallprojects

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from typing import Any
    from xml.etree.ElementTree import Element

    from pypi_typed.types.http import Arguments
    from pypi_typed.types.http import AsyncHttpRequest
    from pypi_typed.types.http import RequestResponse
    from pypi_typed.types.http import SyncHttpRequest
    from pypi_typed.types.types import DistributionsForProjectResponse
    from pypi_typed.types.types import ListAllProjectsResponse
    from pypi_typed.types.types import ProjectResponse
    from pypi_typed.types.types import ProjectStatsResponse
    from pypi_typed.types.types import ProvenanceForFileResponse
    from pypi_typed.types.types import ReleaseResponse
    from pypi_typed.types.types import RSSFeedResponse

    T = TypeVar("T")
    R = TypeVar("R")
HttpRequest = TypeVar(
    "HttpRequest",
    "AsyncHttpRequest",
    "SyncHttpRequest",
)


async def amap(item: Awaitable[T], mapper: Callable[[T], R]) -> R:
    r = await item
    return mapper(r)


@overload
def helper(
    client: SyncHttpRequest, r: Arguments, mapper: Callable[[RequestResponse], R]
) -> R | Awaitable[R]: ...
@overload
def helper(
    client: AsyncHttpRequest, r: Arguments, mapper: Callable[[RequestResponse], R]
) -> R | Awaitable[R]: ...


def helper(
    client: HttpRequest, r: Arguments, mapper: Callable[[RequestResponse], R]
) -> R | Awaitable[R]:
    e = client(**r)
    if isawaitable(e):
        return amap(e, mapper)
    return mapper(e)


def html_json_response_handler(text: str, parser: Callable[[str], T]) -> T:
    try:
        return json.loads(text)  # zuban: ignore[no-any-return]
    except json.JSONDecodeError:
        return parser(text)


@dataclass
class PypiIndexClient(Generic[HttpRequest]):
    ############################################################################
    # region: Index API
    ############################################################################
    """
    https://docs.pypi.org/api/index-api/
    """

    client: HttpRequest
    output: Literal["json", "html"] = "json"

    @overload
    def list_all_projects(self: PypiIndexClient[SyncHttpRequest]) -> ListAllProjectsResponse: ...
    @overload
    def list_all_projects(
        self: PypiIndexClient[AsyncHttpRequest],
    ) -> Awaitable[ListAllProjectsResponse]: ...

    def list_all_projects(self) -> ListAllProjectsResponse | Awaitable[ListAllProjectsResponse]:
        """
        https://docs.pypi.org/api/index-api/#list-all-projects
        """
        args: Arguments = {
            "method": "GET",
            "url": "/simple/",
            "headers": {"Accept": f"application/vnd.pypi.simple.v1+{self.output}"},
        }
        return helper(
            self.client, args, lambda x: html_json_response_handler(x.text, html_to_listallprojects)
        )

    @overload
    def get_distributions_for_project(
        self: PypiIndexClient[SyncHttpRequest], project: str
    ) -> DistributionsForProjectResponse: ...
    @overload
    def get_distributions_for_project(
        self: PypiIndexClient[AsyncHttpRequest], project: str
    ) -> Awaitable[DistributionsForProjectResponse]: ...

    def get_distributions_for_project(
        self, project: str
    ) -> DistributionsForProjectResponse | Awaitable[DistributionsForProjectResponse]:
        """
        https://docs.pypi.org/api/index-api/#get-distributions-for-project
        """
        args: Arguments = {
            "method": "GET",
            "url": f"/simple/{project}/",
            "headers": {"Accept": f"application/vnd.pypi.simple.v1+{self.output}"},
        }
        return helper(
            self.client, args, lambda x: html_json_response_handler(x.text, html_to_distribution)
        )

    ############################################################################
    # endregion: Index API
    ############################################################################


@dataclass
class PypiJsonClient(Generic[HttpRequest]):
    ############################################################################
    # region: JSON API
    ############################################################################
    """
    https://docs.pypi.org/api/json/
    """

    client: HttpRequest

    @overload
    def get_a_project(self: PypiJsonClient[SyncHttpRequest], project: str) -> ProjectResponse: ...
    @overload
    def get_a_project(
        self: PypiJsonClient[AsyncHttpRequest], project: str
    ) -> Awaitable[ProjectResponse]: ...

    def get_a_project(self, project: str) -> ProjectResponse | Awaitable[ProjectResponse]:
        """
        https://docs.pypi.org/api/json/#get-a-project
        """
        args: Arguments = {
            "method": "GET",
            "url": f"/pypi/{project}/json",
            "headers": {"Accept": "application/json"},
        }
        return helper(self.client, args, lambda x: json.loads(x.text))

    @overload
    def get_a_release(
        self: PypiJsonClient[SyncHttpRequest], project: str, version: str
    ) -> ReleaseResponse: ...
    @overload
    def get_a_release(
        self: PypiJsonClient[AsyncHttpRequest], project: str, version: str
    ) -> Awaitable[ReleaseResponse]: ...

    def get_a_release(
        self, project: str, version: str
    ) -> ReleaseResponse | Awaitable[ReleaseResponse]:
        """
        https://docs.pypi.org/api/json/#get-a-release
        """
        args: Arguments = {
            "method": "GET",
            "url": f"/pypi/{project}/{version}/json",
            "headers": {"Accept": "application/json"},
        }
        return helper(self.client, args, lambda x: json.loads(x.text))

    ############################################################################
    # endregion: JSON API
    ############################################################################


@dataclass
class PypiIntegrityClient(Generic[HttpRequest]):
    ############################################################################
    # region: Integrity API
    ############################################################################
    """
    https://docs.pypi.org/api/integrity/
    """

    client: HttpRequest

    @overload
    def get_provenance_for_file(
        self: PypiIntegrityClient[SyncHttpRequest], project: str, version: str, filename: str
    ) -> ProvenanceForFileResponse: ...
    @overload
    def get_provenance_for_file(
        self: PypiIntegrityClient[AsyncHttpRequest], project: str, version: str, filename: str
    ) -> Awaitable[ProvenanceForFileResponse]: ...

    def get_provenance_for_file(
        self, project: str, version: str, filename: str
    ) -> ProvenanceForFileResponse | Awaitable[ProvenanceForFileResponse]:
        """
        https://docs.pypi.org/api/integrity/#get-provenance-for-file
        """
        args: Arguments = {
            "method": "GET",
            "url": f"/integrity/{project}/{version}/{filename}/provenance",
            "headers": {"Accept": "application/vnd.pypi.integrity.v1+json"},
        }
        return helper(self.client, args, lambda x: json.loads(x.text))

    ############################################################################
    # endregion: Integrity API
    ############################################################################


@dataclass
class PypiStatsClient(Generic[HttpRequest]):
    ############################################################################
    # region: Stats API
    ############################################################################
    """
    https://docs.pypi.org/api/stats/
    """

    client: HttpRequest

    @overload
    def project_stats(self: PypiStatsClient[SyncHttpRequest]) -> ProjectStatsResponse: ...
    @overload
    def project_stats(
        self: PypiStatsClient[AsyncHttpRequest],
    ) -> Awaitable[ProjectStatsResponse]: ...

    def project_stats(self) -> ProjectStatsResponse | Awaitable[ProjectStatsResponse]:
        """
        https://docs.pypi.org/api/stats/#project-stats
        """
        args: Arguments = {
            "method": "GET",
            "url": "/stats/",
            "headers": {"Accept": "application/json"},
        }
        return helper(self.client, args, lambda x: json.loads(x.text))

    ############################################################################
    # endregion: Stats API
    ############################################################################


def parse_xml_node(element: Element) -> Any:  # noqa: ANN401
    """
    Recursively parse an XML element into a plain Python structure.

    - Element with only text → returns the stripped text string (or None)
    - Element with child elements → returns a dict; repeated tags become lists
    - Element with both text and children → text is stored under the "_text" key
    - Attributes are stored under the "_attrs" key (omitted when empty)
    """
    result: dict[str, Any] = {}

    # Attach attributes if present
    if element.attrib:
        result["_attrs"] = dict(element.attrib)

    # Recurse into children
    for child in element:
        # Strip namespace, e.g. "{http://...}tag" → "tag"
        tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag
        value = parse_xml_node(child)

        if tag in result:
            # Promote to list on first collision, then append
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value

    # Handle text content
    text = (element.text or "").strip()
    if text:
        if result:
            # Mixed content: keep text alongside children
            result["_text"] = text
        else:
            # Leaf node: return the text directly (clean and simple)
            return text

    return result or None


def parse_xml_response(xml_string: str) -> RSSFeedResponse:
    """
    Parse an XML string into a nested dict / list structure.
    Returns a dict with the root tag as the single top-level key.
    """
    from xml.etree.ElementTree import fromstring

    root = fromstring(xml_string)  # noqa: S314
    tag = root.tag.split("}", 1)[-1] if "}" in root.tag else root.tag
    if tag != "rss":
        msg = f"Expected root tag 'rss', got '{tag}'"
        raise ValueError(msg)
    return {tag: parse_xml_node(root)}  # type: ignore[misc]


@dataclass
class RSSFeedsClient(Generic[HttpRequest]):
    ############################################################################
    # region: RSS Feeds
    ############################################################################
    """
    https://docs.pypi.org/api/feeds/
    """

    client: HttpRequest

    @overload
    def newest_packages_feed(
        self: RSSFeedsClient[SyncHttpRequest],
    ) -> RSSFeedResponse: ...
    @overload
    def newest_packages_feed(
        self: RSSFeedsClient[AsyncHttpRequest],
    ) -> Awaitable[RSSFeedResponse]: ...

    def newest_packages_feed(
        self,
    ) -> RSSFeedResponse | Awaitable[RSSFeedResponse]:
        """
        https://docs.pypi.org/api/feeds/#newest-packages-feed
        """
        args: Arguments = {
            "method": "GET",
            "url": "/rss/packages.xml",
        }
        return helper(
            self.client,
            args,
            lambda x: parse_xml_response(x.text),
        )

    @overload
    def latest_updates_feed(
        self: RSSFeedsClient[SyncHttpRequest],
    ) -> RSSFeedResponse: ...
    @overload
    def latest_updates_feed(
        self: RSSFeedsClient[AsyncHttpRequest],
    ) -> Awaitable[RSSFeedResponse]: ...

    def latest_updates_feed(
        self,
    ) -> RSSFeedResponse | Awaitable[RSSFeedResponse]:
        """
        https://docs.pypi.org/api/feeds/#latest-updates-feed
        """
        args: Arguments = {
            "method": "GET",
            "url": "/rss/updates.xml",
        }
        return helper(
            self.client,
            args,
            lambda x: parse_xml_response(x.text),
        )

    @overload
    def project_releases_feed(
        self: RSSFeedsClient[SyncHttpRequest],
        project_name: str,
    ) -> RSSFeedResponse: ...
    @overload
    def project_releases_feed(
        self: RSSFeedsClient[AsyncHttpRequest],
        project_name: str,
    ) -> Awaitable[RSSFeedResponse]: ...

    def project_releases_feed(
        self,
        project_name: str,
    ) -> RSSFeedResponse | Awaitable[RSSFeedResponse]:
        """
        https://docs.pypi.org/api/feeds/#project-releases-feed
        """
        args: Arguments = {
            "method": "GET",
            "url": f"/rss/project/{project_name}/releases.xml",
        }
        return helper(
            self.client,
            args,
            lambda x: parse_xml_response(x.text),
        )

    ############################################################################
    # endregion: RSS Feeds
    ############################################################################


# class PyPiUploadAPI: ...
# BigQuery Datasets
# Secret reporting API


@dataclass
class PypiApiClient(
    PypiIndexClient[HttpRequest],
    PypiJsonClient[HttpRequest],
    PypiIntegrityClient[HttpRequest],
    PypiStatsClient[HttpRequest],
    RSSFeedsClient[HttpRequest],
): ...


if __name__ == "__main__":  # pragma: no cover

    async def main() -> None:
        import httpx

        # base_url = "https://pypi.devinfra.sentry.io/"
        # base_url = "https://flavioamurriocs.github.io/pypi/"
        base_url = "https://pypi.org/"
        combined: PypiApiClient[AsyncHttpRequest] = PypiApiClient(
            client=httpx.AsyncClient(base_url=base_url).request
        )
        # e = await combined.json.get_a_project("uv-to-pipfile")
        # e = await combined.list_all_projects()
        # e = await combined.project_releases_feed("uv-to-pipfile")
        e = await combined.newest_packages_feed()
        print(e)

    import asyncio

    asyncio.run(main())

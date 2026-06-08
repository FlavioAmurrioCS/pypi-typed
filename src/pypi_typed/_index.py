from __future__ import annotations

import re
from contextlib import suppress
from html import unescape
from html.parser import HTMLParser
from typing import TYPE_CHECKING
from typing import Literal

if TYPE_CHECKING:
    from pypi_typed.types.types import DistributionsForProjectResponse
    from pypi_typed.types.types import ListAllProjectsResponse
    from pypi_typed.types.types import _DistributionsForProjectResponseFile


MISSING_SERIAL = -1


class PypiIndexParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.meta: dict[str, str] = {}
        self._in_title: bool = False
        self.title: str = ""
        self._in_a_tag: bool = False
        self.current_a_tag: dict[str, str | None] | None = None
        self.a_tags: list[dict[str, str | None]] = []
        self.serial: int = MISSING_SERIAL

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "meta":
            dct = dict(attrs)
            self.meta[dct.get("name") or ""] = dct.get("content") or ""
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            self._in_a_tag = True
            self.current_a_tag = dict(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "a":
            self._in_a_tag = False
            if self.current_a_tag:
                self.a_tags.append(self.current_a_tag)
            self.current_a_tag = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif self._in_a_tag and self.current_a_tag:
            self.current_a_tag["_text"] = (self.current_a_tag.get("_text") or "") + data

    def handle_comment(self, data: str) -> None:
        txt = data.strip()
        if txt.startswith("SERIAL "):
            with suppress(ValueError):
                self.serial = int(txt.split(" ", maxsplit=1)[-1].strip())


def html_to_distribution(
    html_text: str,
) -> DistributionsForProjectResponse:
    parser = PypiIndexParser()
    parser.feed(html_text)

    title = parser.title
    name = title.replace("Links for ", "") if title else ""

    api_version = parser.meta.get("pypi:repository-version") or "1.0"
    project_status = parser.meta.get("pypi:project-status") or "unknown"

    serial = parser.serial

    files = [_extract_file_metadata(link) for link in parser.a_tags]

    versions: set[str] = set()
    for file in files:
        version = _get_version(file["filename"])
        if version:
            versions.add(version)

    return {
        "alternate-locations": [],
        "files": files,
        "meta": {
            "_last-serial": serial,
            "api-version": api_version,
        },
        "name": name,
        "project-status": {"status": project_status},
        "versions": sorted(versions),
    }


def html_to_listallprojects(html_text: str) -> ListAllProjectsResponse:
    parser = PypiIndexParser()
    parser.feed(html_text)

    return {
        "meta": {
            "_last-serial": parser.serial,
            "api-version": parser.meta.get("pypi:repository-version") or "1.0",
        },
        "projects": [
            {
                "name": (
                    x.get("_text")
                    or (x.get("href") or "")
                    .removesuffix("index.html")
                    .rstrip("/")
                    .rsplit("/", maxsplit=1)[-1]
                ),
                "_last-serial": MISSING_SERIAL,
            }
            for x in parser.a_tags
        ],
    }


def _extract_file_metadata(link: dict[str, str | None]) -> _DistributionsForProjectResponseFile:
    href = link.get("href") or ""
    url, _, hash_fragment = href.partition("#")
    hash_value: dict[str, str] = {}
    if hash_fragment.startswith("sha256="):
        hash_value = {"sha256": hash_fragment[7:]}

    data_dist_info = link.get("data-dist-info-metadata")
    data_dist_info_value: dict[str, str] | Literal[False] = False
    if data_dist_info:
        data_dist_info = data_dist_info.removeprefix("sha256=")
        data_dist_info_value = {"sha256": data_dist_info}

    core_metadata = link.get("data-core-metadata")
    core_metadata_value: dict[str, str] | Literal[False] = False
    if core_metadata:
        core_metadata = core_metadata.removeprefix("sha256=")
        core_metadata_value = {"sha256": core_metadata}

    requires_python = link.get("data-requires-python")
    if requires_python:
        requires_python = unescape(requires_python)

    yanked_value = link.get("data-yanked")
    yanked: bool | str = False
    if yanked_value is not None:
        yanked = yanked_value or True

    provenance = link.get("data-provenance")

    return {
        "filename": link.get("_text") or "",
        "url": url,
        "hashes": hash_value,
        "requires-python": requires_python,
        "size": 0,
        "upload-time": "",
        "yanked": yanked,
        "data-dist-info-metadata": data_dist_info_value,
        "core-metadata": core_metadata_value,
        "provenance": provenance,
    }


def _get_version(filename: str) -> str | None:
    size = 2
    if filename.endswith(".whl"):
        parts = filename.split("-")
        return parts[1] if len(parts) >= size and parts[-1] == ".whl" else None

    base = filename
    for ext in (".tar.gz", ".tgz", ".zip", ".exe"):
        if base.endswith(ext):
            base = base[: -len(ext)]
            break
    parts = base.split("-")
    if len(parts) < size:
        return None
    version = parts[1]
    return re.sub(r"\.win.*$", "", version)

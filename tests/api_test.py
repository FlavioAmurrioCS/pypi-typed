from __future__ import annotations

import asyncio
import json
import os
from typing import TYPE_CHECKING

import httpx
import pytest
from persistent_cache.decorators import sqlite_cache
from pydantic import TypeAdapter

from pypi_typed.api import PypiApiClient
from pypi_typed.types.types import DistributionsForProjectResponse
from pypi_typed.types.types import ListAllProjectsResponse
from pypi_typed.types.types import ProjectResponse
from pypi_typed.types.types import ProjectStatsResponse
from pypi_typed.types.types import ProvenanceForFileResponse
from pypi_typed.types.types import ReleaseResponse

if TYPE_CHECKING:
    from typing import Literal
    from typing import TypeVar

    from pypi_typed.types.http import AsyncHttpRequest

    T = TypeVar("T")

projects = [
    "aiobotocore",
    "beautifulsoup4",
    "boto3",
    "botocore",
    "certifi",
    "cffi",
    "click",
    "cryptography",
    "flask",
    "idna",
    "packaging",
    "pandas",
    "pip",
    "pycparser",
    "pydantic",
    "pygments",
    "requests",
    "scipy",
    "six",
    "typing-extensions",
    "virtualenv",
    "uv-to-pipfile",
]
projects = [
    "aws-http-auth",
    "comma-cli",
    "depsdev",
    "dev-toolbox",
    "direct-deps",
    "lambda-dev-server",
    "log-tool",
    "persistent-cache-decorator",
    "runtool",
    "typedfzf",
    "uv-to-pipfile",
]

projects_versions = [("lambda-dev-server", "0.0.8")]
project_version_filenames = [
    ("lambda-dev-server", "0.0.8", "lambda_dev_server-0.0.8-py3-none-any.whl")
]


def validate_shape(obj: object, _type: type[T]) -> T:
    return TypeAdapter(_type).validate_python(obj, extra="forbid", strict=True)


def create_async_client(
    base_url: str, output: Literal["json", "html"] = "json"
) -> PypiApiClient[AsyncHttpRequest]:
    async_client = httpx.AsyncClient(base_url=base_url)
    request_func = async_client.request
    async_client.send = sqlite_cache(days=1)(async_client.send)  # type: ignore[method-assign,unused-ignore]
    return PypiApiClient(client=request_func, output=output)


INDEX_PYPI = "https://pypi.org/"
INDEX_FLAVIO = "https://flavioamurriocs.github.io/pypi/"
INDEX_SENTRY = "https://pypi.devinfra.sentry.io/"


@pytest.mark.parametrize("base_url", [INDEX_PYPI, INDEX_FLAVIO, INDEX_SENTRY])
@pytest.mark.parametrize("output", ["json", "html"])
async def test_types_list_all_projects(base_url: str, output: Literal["json", "html"]) -> None:
    pypi_api_client = create_async_client(base_url=base_url, output=output)
    response = await pypi_api_client.list_all_projects()
    write_data_to_file(data=response, base_url=base_url, output=output, api="list-all-projects")
    validate_shape(response, ListAllProjectsResponse)


@pytest.mark.parametrize("base_url", [INDEX_PYPI, INDEX_FLAVIO])
@pytest.mark.parametrize("output", ["json", "html"])
@pytest.mark.parametrize("project", projects)
async def test_types_get_distributions_for_project(
    base_url: str, output: Literal["json", "html"], project: str
) -> None:
    pypi_api_client = create_async_client(base_url=base_url, output=output)
    response = await pypi_api_client.get_distributions_for_project(project=project)
    write_data_to_file(
        data=response,
        base_url=base_url,
        output=output,
        api="get-distributions-for-project",
        project=project,
    )
    validate_shape(response, DistributionsForProjectResponse)


@pytest.mark.parametrize(
    "base_url",
    [
        INDEX_PYPI,
        # INDEX_FLAVIO,  # SKIP FOR NOW UNTIL TYPES ARE CEMENTED
    ],
)
@pytest.mark.parametrize("project", ["uv-to-pipfile"])
async def test_types_get_a_project(base_url: str, project: str) -> None:
    pypi_api_client = create_async_client(base_url=base_url, output="json")
    response = await pypi_api_client.get_a_project(project=project)
    write_data_to_file(
        data=response, base_url=base_url, output="json", api="get-a-project", project=project
    )
    validate_shape(response, ProjectResponse)


@pytest.mark.parametrize(
    "base_url",
    [
        INDEX_PYPI,
        # INDEX_FLAVIO,  # SKIP FOR NOW UNTIL TYPES ARE CEMENTED
    ],
)
@pytest.mark.parametrize(("project", "version"), projects_versions)
async def test_types_get_a_release(base_url: str, project: str, version: str) -> None:
    pypi_api_client = create_async_client(base_url=base_url, output="json")
    response = await pypi_api_client.get_a_release(project=project, version=version)
    write_data_to_file(
        data=response,
        base_url=base_url,
        output="json",
        api="get-a-release",
        project=project,
        version=version,
    )
    validate_shape(response, ReleaseResponse)


@pytest.mark.parametrize("base_url", [INDEX_PYPI])
@pytest.mark.parametrize(("project", "version", "filename"), project_version_filenames)
async def test_types_get_provenance_for_file(
    base_url: str, project: str, version: str, filename: str
) -> None:
    pypi_api_client = create_async_client(base_url=base_url)
    response = await pypi_api_client.get_provenance_for_file(
        project=project,
        version=version,
        filename=filename,
    )
    write_data_to_file(
        data=response,
        base_url=base_url,
        output="json",
        api="provenance-for-file",
        project=project,
        version=version,
        filename=filename,
    )
    validate_shape(response, ProvenanceForFileResponse)


@pytest.mark.parametrize("base_url", [INDEX_PYPI])
async def test_types_project_stats(base_url: str) -> None:
    pypi_api_client = create_async_client(base_url=base_url)
    response = await pypi_api_client.project_stats()
    write_data_to_file(data=response, base_url=base_url, output="json", api="project-stats")
    validate_shape(response, ProjectStatsResponse)


async def test_parity_list_all_projects() -> None:
    html_client = create_async_client(INDEX_PYPI, output="html")
    json_client = create_async_client(INDEX_PYPI, output="json")
    html_response, json_response = await asyncio.gather(
        html_client.list_all_projects(), json_client.list_all_projects()
    )

    write_data_to_file(
        data=html_response, base_url=INDEX_PYPI, output="html", api="list-all-projects"
    )
    write_data_to_file(
        data=json_response, base_url=INDEX_PYPI, output="json", api="list-all-projects"
    )
    # We expect html and json responses to be different,
    # if they are the same it means json endpoint is returning html instead of json
    assert html_response != json_response

    html_names = {x["name"] for x in html_response["projects"]}
    json_names = {x["name"] for x in json_response["projects"]}
    common_names = html_names & json_names
    only_html_names = html_names - json_names
    only_json_names = json_names - html_names

    # print()
    # print(f"Only in HTML: {len(only_html_names)=} {sorted(only_html_names)}")
    # print(f"Only in JSON: {len(only_json_names)=} {sorted(only_json_names)}")
    diff_limit = 100
    assert len(only_html_names) < diff_limit
    assert len(only_json_names) < diff_limit

    json_response["projects"] = sorted(
        (p for p in json_response["projects"] if p["name"] in common_names), key=lambda x: x["name"]
    )
    html_response["projects"] = sorted(
        (p for p in html_response["projects"] if p["name"] in common_names), key=lambda x: x["name"]
    )
    for p in json_response["projects"]:
        p.pop("_last-serial", None)  # type: ignore[misc]
    for p in html_response["projects"]:
        p.pop("_last-serial", None)  # type: ignore[misc]
    html_response["meta"].pop("_last-serial", None)  # type: ignore[misc]
    json_response["meta"].pop("_last-serial", None)  # type: ignore[misc]

    assert html_response == json_response


@pytest.mark.parametrize("project", projects)
async def test_parity_get_distributions_for_project(project: str) -> None:
    html_client = create_async_client(INDEX_PYPI, output="html")
    json_client = create_async_client(INDEX_PYPI, output="json")
    html_response, json_response = await asyncio.gather(
        html_client.get_distributions_for_project(project=project),
        json_client.get_distributions_for_project(project=project),
    )
    write_data_to_file(
        data=html_response,
        base_url=INDEX_PYPI,
        output="html",
        api="distributions-for-project",
        project=project,
    )
    write_data_to_file(
        data=json_response,
        base_url=INDEX_PYPI,
        output="json",
        api="distributions-for-project",
        project=project,
    )

    # We expect html and json responses to be different,
    # if they are the same it means json endpoint is returning html instead of json
    assert html_response != json_response

    for file in html_response["files"]:
        file.pop("upload-time", None)  # type: ignore[misc]
        file.pop("size", None)  # type: ignore[misc]
    for file in json_response["files"]:
        file.pop("upload-time", None)  # type: ignore[misc]
        file.pop("size", None)  # type: ignore[misc]

    html_response["versions"].sort()
    json_response["versions"].sort()

    assert html_response == json_response


log_to_file = False


def write_data_to_file(  # noqa: PLR0913
    *,
    data: object,
    base_url: str,
    output: str,
    api: str,
    project: str = "",
    version: str = "",
    filename: str = "",
) -> None:
    if log_to_file:
        filename = f"/tmp/pypi_files/{base_url.replace('/', '_')}/{api}/{output}/{project}_{version}_{filename}.json"  # noqa: E501, S108
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

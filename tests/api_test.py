from __future__ import annotations

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
    from pypi_typed.types.http import AsyncHttpRequest

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
]
projects_versions = [("virtualenv", "21.2.4")]
project_version_filenames = [("virtualenv", "21.2.4", "virtualenv-21.2.4-py3-none-any.whl")]


@pytest.fixture
def pypi_api_client() -> PypiApiClient[AsyncHttpRequest]:
    async_client = httpx.AsyncClient(base_url="https://pypi.org")
    return PypiApiClient(client=sqlite_cache(days=1)(async_client.request))


async def test_list_all_projects_types(pypi_api_client: PypiApiClient[AsyncHttpRequest]) -> None:
    response = await pypi_api_client.list_all_projects()
    TypeAdapter(ListAllProjectsResponse).validate_python(response, extra="forbid", strict=True)


# @pytest.mark.asyncio
@pytest.mark.parametrize("project", projects)
async def test_get_a_project_types(
    pypi_api_client: PypiApiClient[AsyncHttpRequest], project: str
) -> None:
    response = await pypi_api_client.get_a_project(project=project)
    TypeAdapter(ProjectResponse).validate_python(response, extra="forbid", strict=True)


@pytest.mark.parametrize("project", projects)
async def test_get_distributions_for_project_types(
    pypi_api_client: PypiApiClient[AsyncHttpRequest], project: str
) -> None:
    response = await pypi_api_client.get_distributions_for_project(project=project)
    TypeAdapter(DistributionsForProjectResponse).validate_python(
        response, extra="forbid", strict=True
    )


@pytest.mark.parametrize("project_version", projects_versions)
async def test_get_a_release_types(
    pypi_api_client: PypiApiClient[AsyncHttpRequest], project_version: tuple[str, str]
) -> None:
    response = await pypi_api_client.get_a_release(
        project=project_version[0], version=project_version[1]
    )
    TypeAdapter(ReleaseResponse).validate_python(response, extra="forbid", strict=True)


@pytest.mark.parametrize("project_version_filename", project_version_filenames)
async def test_get_provenance_for_file_types(
    pypi_api_client: PypiApiClient[AsyncHttpRequest],
    project_version_filename: tuple[str, str, str],
) -> None:
    response = await pypi_api_client.get_provenance_for_file(
        project=project_version_filename[0],
        version=project_version_filename[1],
        filename=project_version_filename[2],
    )
    TypeAdapter(ProvenanceForFileResponse).validate_python(response, extra="forbid", strict=True)


async def test_project_stats_types(pypi_api_client: PypiApiClient[AsyncHttpRequest]) -> None:
    response = await pypi_api_client.project_stats()
    TypeAdapter(ProjectStatsResponse).validate_python(response, extra="forbid", strict=True)


# @pytest.mark.parametrize("package", packages)
# def test_types(package: str) -> None:
#     """Validate GetDistributionsForProjectResponse from JSON API"""
#     json_data = json.loads(_get_text(f"/simple/{package}/", "json"))
#     TypeAdapter(types.GetDistributionsForProjectResponse).validate_python(json_data)

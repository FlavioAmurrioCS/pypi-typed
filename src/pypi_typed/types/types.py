from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired
from typing_extensions import TypedDict

_ListAllProjectsResponseMeta = TypedDict(
    "_ListAllProjectsResponseMeta",
    {"_last-serial": int, "api-version": str},
)


_ListAllProjectsResponseProject = TypedDict(
    "_ListAllProjectsResponseProject",
    {"_last-serial": int, "name": str},
)


class ListAllProjectsResponse(TypedDict):
    meta: _ListAllProjectsResponseMeta
    projects: list[_ListAllProjectsResponseProject]


class _ReleaseResponseInfo(TypedDict):
    author: str | None
    author_email: str | None
    bugtrack_url: str | None
    classifiers: list[str]
    description: str | None
    description_content_type: str | None
    docs_url: str | None
    download_url: str | None
    downloads: dict[str, int]
    dynamic: list[str] | None
    home_page: str | None
    keywords: str | None
    license: str | None
    license_expression: str | None
    license_files: list[str] | None
    maintainer: str | None
    maintainer_email: str | None
    name: str
    package_url: str
    platform: str | None
    project_url: str
    project_urls: dict[str, str]
    provides_extra: list[str] | None
    release_url: str
    requires_dist: list[str] | None
    requires_python: str | None
    summary: str | None
    version: str
    yanked: bool | None
    yanked_reason: str | None


class _ReleaseResponseUrlFile(TypedDict):
    comment_text: str | None
    digests: dict[str, str]
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: str | None
    size: int
    upload_time: str
    upload_time_iso_8601: str
    url: str
    yanked: bool | str | None
    yanked_reason: str | None


class _ReleaseResponseVulnerability(TypedDict):
    id: str
    link: str
    title: str
    details: str
    aliases: list[str]
    fixed_in: str | None


class _ReleaseResponseOwnershipPublisher(TypedDict):
    role: str
    user: str


class _ReleaseResponseOwnership(TypedDict):
    organization: str | None
    roles: list[_ReleaseResponseOwnershipPublisher]


class ReleaseResponse(TypedDict):
    info: _ReleaseResponseInfo
    last_serial: int
    urls: list[_ReleaseResponseUrlFile]
    vulnerabilities: list[_ReleaseResponseVulnerability]
    ownership: _ReleaseResponseOwnership


class _ProvenanceEnvelope(TypedDict):
    signature: str
    statement: str


class _ProvenanceKindVersion(TypedDict):
    kind: str
    version: str


class _ProvenanceLogId(TypedDict):
    keyId: str


class _ProvenanceInclusionPromise(TypedDict):
    signedEntryTimestamp: str


class _ProvenanceInclusionProof(TypedDict):
    checkpoint: dict[str, str]
    hashes: list[str]
    logIndex: str
    rootHash: str
    treeSize: str


class _ProvenanceTransparencyEntry(TypedDict):
    canonicalizedBody: str
    inclusionPromise: _ProvenanceInclusionPromise
    inclusionProof: _ProvenanceInclusionProof
    integratedTime: str
    kindVersion: _ProvenanceKindVersion
    logId: _ProvenanceLogId
    logIndex: str


class _ProvenanceVerificationMaterial(TypedDict):
    certificate: str
    transparency_entries: list[_ProvenanceTransparencyEntry]


class _ProvenanceAttestation(TypedDict):
    envelope: _ProvenanceEnvelope
    verification_material: _ProvenanceVerificationMaterial
    version: int


class _ProvenancePublisher(TypedDict):
    claims: NotRequired[str | None]
    environment: NotRequired[str | None]
    kind: str
    repository: NotRequired[str | None]
    workflow: NotRequired[str | None]


class _ProvenanceAttestationBundle(TypedDict):
    attestations: list[_ProvenanceAttestation]
    publisher: _ProvenancePublisher


class ProvenanceForFileResponse(TypedDict):
    attestation_bundles: list[_ProvenanceAttestationBundle]
    version: int


class _ProjectStatsResponseTopPackage(TypedDict):
    size: int


class ProjectStatsResponse(TypedDict):
    top_packages: dict[str, _ProjectStatsResponseTopPackage]
    total_packages_size: int


_DistributionsForProjectResponseMeta = TypedDict(
    "_DistributionsForProjectResponseMeta",
    {"_last-serial": int, "api-version": str},
)


class _DistributionsForProjectResponseProjectStatus(TypedDict):
    status: str


# class _DistributionsForProjectResponseHash(TypedDict):
#     sha256: str


# OptionalHash = _DistributionsForProjectResponseHash | Literal[False]
_DistributionsForProjectResponseHash = dict[str, str]
OptionalHash = _DistributionsForProjectResponseHash | Literal[False]


_DistributionsForProjectResponseFile = TypedDict(
    "_DistributionsForProjectResponseFile",
    {
        "core-metadata": OptionalHash,
        "data-dist-info-metadata": OptionalHash,
        "filename": str,
        "hashes": _DistributionsForProjectResponseHash,
        "provenance": str | None,
        "requires-python": str | None,
        "size": int,
        "upload-time": str,
        "url": str,
        "yanked": bool | str,
    },
)


DistributionsForProjectResponse = TypedDict(
    "DistributionsForProjectResponse",
    {
        "alternate-locations": list[str],
        "files": list[_DistributionsForProjectResponseFile],
        "meta": _DistributionsForProjectResponseMeta,
        "name": str,
        "project-status": _DistributionsForProjectResponseProjectStatus,
        "versions": list[str],
    },
)


class _ProjectResponseInfo(TypedDict):
    author: str | None
    author_email: str | None
    bugtrack_url: str | None
    classifiers: list[str]
    description: str | None
    description_content_type: str | None
    docs_url: str | None
    download_url: str | None
    downloads: dict[str, int]
    dynamic: list[str] | None
    home_page: str | None
    keywords: str | None
    license: str | None
    license_expression: str | None
    license_files: list[str] | None
    maintainer: str | None
    maintainer_email: str | None
    name: str
    package_url: str
    platform: str | None
    project_url: str
    project_urls: dict[str, str]
    provides_extra: list[str] | None
    release_url: str
    requires_dist: list[str] | None
    requires_python: str | None
    summary: str | None
    version: str
    yanked: bool | None
    yanked_reason: str | None


class _ProjectResponseUrlFileDigests(TypedDict):
    sha256: str
    md5: str
    blake2b_256: str | None


class _ProjectResponseUrlFile(TypedDict):
    comment_text: str | None
    digests: _ProjectResponseUrlFileDigests
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: str | None
    size: int
    upload_time: str
    upload_time_iso_8601: str
    url: str
    yanked: bool | str | None
    yanked_reason: str | None


class _ProjectResponseVulnerability(TypedDict):
    id: str
    link: str
    title: str
    details: str
    aliases: list[str]
    fixed_in: str | None


class _ProjectResponseOwnershipRole(TypedDict):
    role: str
    user: str


class _ProjectResponseOwnership(TypedDict):
    organization: str | None
    roles: list[_ProjectResponseOwnershipRole]


class ProjectResponse(TypedDict):
    info: _ProjectResponseInfo
    last_serial: int
    releases: dict[str, list[_ProjectResponseUrlFile]]
    urls: list[_ProjectResponseUrlFile]
    vulnerabilities: list[_ProjectResponseVulnerability]
    ownership: _ProjectResponseOwnership

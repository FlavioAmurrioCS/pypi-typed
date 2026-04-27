from __future__ import annotations

import argparse
import asyncio
import json
import logging
from textwrap import dedent
from typing import TYPE_CHECKING
from typing import NamedTuple

import httpx

from pypi_typed.api import PypiApiClient

if TYPE_CHECKING:
    from typing_extensions import Protocol

    from pypi_typed.types.http import AsyncHttpRequest

    class Cmd(Protocol):
        @classmethod
        def arg_parser(
            cls, parser: argparse.ArgumentParser | None = None
        ) -> argparse.ArgumentParser: ...
        async def run(self) -> int: ...


logger = logging.getLogger(__name__)
HTTPX_CLIENT = httpx.AsyncClient(base_url="https://pypi.org/")
CLIENT: PypiApiClient[AsyncHttpRequest] = PypiApiClient(client=HTTPX_CLIENT.request)


class SampleCmd(NamedTuple):
    """<Brief description of the command>."""

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        return parser

    async def run(self) -> int:
        print(f"Executing {self}...")
        return 0


class ListAllProjectsCmd(NamedTuple):
    """List all projects."""

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        return parser

    async def run(self) -> int:
        response = await CLIENT.list_all_projects()
        for project in response["projects"]:
            print(project["name"])
        return 0


class DistributionsForProjectCmd(NamedTuple):
    """List all distributions for a project."""

    project: str

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        parser.add_argument("project", help="The name of the project to list distributions for.")
        return parser

    async def run(self) -> int:
        response = await CLIENT.get_distributions_for_project(self.project)
        print(json.dumps(response, indent=2))
        return 0


class ProjectCmd(NamedTuple):
    """Get details of a specific project."""

    project: str

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        parser.add_argument("project", help="The name of the project to get details for.")
        return parser

    async def run(self) -> int:
        response = await CLIENT.get_a_project(self.project)
        print(json.dumps(response, indent=2))
        return 0


class ReleaseCmd(NamedTuple):
    """Get details of a specific release for a project."""

    project: str
    version: str

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        parser.add_argument("project", help="The name of the project to get the release for.")
        parser.add_argument("version", help="The version of the project to get the release for.")
        return parser

    async def run(self) -> int:
        response = await CLIENT.get_a_release(self.project, self.version)
        print(json.dumps(response, indent=2))
        return 0


class ProvenanceForFileCmd(NamedTuple):
    """Get details of a specific file's provenance for a project."""

    project: str
    version: str
    filename: str

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        parser.add_argument(
            "project", help="The name of the project to get the file's provenance for."
        )
        parser.add_argument(
            "version", help="The version of the project to get the file's provenance for."
        )
        parser.add_argument("filename", help="The name of the file to get the provenance for.")
        return parser

    async def run(self) -> int:
        response = await CLIENT.get_provenance_for_file(self.project, self.version, self.filename)
        print(json.dumps(response, indent=2))
        return 0


class ProjectStatsCmd(NamedTuple):
    """Get statistics of a specific project."""

    @classmethod
    def arg_parser(cls, parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
        parser = parser or argparse.ArgumentParser()
        parser.description = cls.__doc__ or "<PLACEHOLDER_DESCRIPTION>"
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.epilog = dedent("""\
        Example:
          %(prog)s <PLACEHOLDER_EXAMPLE>
        """)
        return parser

    async def run(self) -> int:
        response = await CLIENT.project_stats()
        print(json.dumps(response, indent=2))
        return 0


################################################################################
# endregion: Commands
################################################################################

SUB_COMMANDS: dict[str, type[Cmd]] = {
    "list-all-projects": ListAllProjectsCmd,
    "distributions-for-project": DistributionsForProjectCmd,
    "project": ProjectCmd,
    "release": ReleaseCmd,
    "provenance-for-file": ProvenanceForFileCmd,
    "project-stats": ProjectStatsCmd,
}

VERSION = "0.1.0"


async def main(argv: list[str] | tuple[str, ...] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.description = "CLI Example with subcommands"
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.epilog = dedent("""\
    Example:
      %(prog)s hello
    """)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity level."
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    parser.add_argument(
        "--base-url",
        default="https://pypi.org/",
        help="Base URL for the PyPI API (default: https://pypi.org/).",
    )

    subparsers = parser.add_subparsers(dest="command")
    for cmd_name, cmd in SUB_COMMANDS.items():
        cmd_parser = subparsers.add_parser(cmd_name, help=cmd.__doc__ or None)
        cmd.arg_parser(cmd_parser)
    args = parser.parse_args(argv)
    command: str | None = args.command
    verbose: int = args.verbose
    if command is None:
        # NOTE: You can also set a default command here if desired
        parser.print_help()
        return 1
    logging.basicConfig(
        level=logging.WARNING - (verbose * 10),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    cls = SUB_COMMANDS[command]

    excluded_args = ("command", "verbose", "base_url")
    cmd_instance = cls(**{k: v for k, v in vars(args).items() if k not in excluded_args})
    HTTPX_CLIENT.base_url = args.base_url
    return await cmd_instance.run()


def main_sync(argv: list[str] | tuple[str, ...] | None = None) -> int:
    return asyncio.run(main(argv))


if __name__ == "__main__":
    raise SystemExit(main_sync())

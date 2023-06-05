import argparse
import subprocess
import typing

from utils import known_projects

class ClearCacheCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("clear-cache", help="Removes all known projects from the local Conan cache.")
        p.set_defaults(func=ClearCacheCommand.run)

    @staticmethod
    def run(_) -> typing.Iterable[str]:
        for p in known_projects:
            print(f"Removing {p}.")
            subprocess.check_call(["conan", "remove", "-c", f"{p}/*"])

import argparse
import os
import typing

from gitutils import GitUtils
from utils import known_projects, filter_known_projects, get_config

class CloneCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("clone", help="Clones all known or explicitly specified projects.")
        p.add_argument("--projects", nargs="*", required=False, help="List of projects that are retrieved. If empty,\
                       all known projects are retrieved. To clone specific projects and specific tags, use\
                       'project/tag'.")
    
        p.set_defaults(func=CloneCommand.run)
    
    @staticmethod
    def run(args) -> typing.Iterable[str]:
        """
        Clone all known projects. Defaults to trunk branch for all projects, unless otherwise specified.
        """

        if args.projects:
            projects = filter_known_projects(args.projects)
        else:
            projects = known_projects

        problems = []

        config = get_config()

        for p in projects:
            source = os.path.join(config["default"]["projectdir"], p, "source")
            GitUtils.open_or_clone_project(p, source, config)

        return problems

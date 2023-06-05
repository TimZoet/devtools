import argparse
import typing

from conanutils import ConanUtils
from utils import get_config, filter_known_projects, known_projects

class ExportCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("export", help="Exports packages to the local Conan cache.")
        p.add_argument("--projects", nargs="*", required=False, help="List of projects that are exported to the Conan\
                       cache. If empty, all known projects are exported. To export specific projects and specific tags,\
                       use 'project/tag'.")
        p.set_defaults(func=ExportCommand.run)
    
    @staticmethod
    def run(args) -> typing.Iterable[str]:
        if args.projects:
            projects = filter_known_projects(args.projects)
        else:
            projects = known_projects

        problems = []

        config = get_config()

        for p in projects:
            success, err = ConanUtils.export(config, p)
            if not success:
                problems.append(err)

        return problems

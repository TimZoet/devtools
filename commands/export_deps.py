import argparse
import os
import re
import subprocess
import tempfile
import typing

from conan.api.conan_api import ConanAPI
from conans.client.graph.graph_error import GraphMissingError
from conans.errors import ConanException

from utils import get_config, get_arg_project

class ExportDepsCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("export-deps", help="Automatically resolves all required packages for a single project\
                              and exports them to the local Conan cache.")
        p.add_argument("--project", dest="project", required=False, help="Project name. If not set, will try to derive\
                       current project from working directory.")
        p.add_argument("--profile", dest="profile", required=True, help="Name of profile. Can be a profile stored in\
                       the Conan cache, or in the current projects' buildtools/profiles folder. The latter takes\
                       precedence.")
        p.set_defaults(func=ExportDepsCommand.run)

    @staticmethod
    def run(args) -> typing.Iterable[str]:
        config = get_config()

        problems = []

        known, project, tag = get_arg_project(args)
        if not known:
            problems.append(f"Unknown project {project}.")
            return problems

        # TODO: Use tag.

        api = ConanAPI()
        remotes = api.remotes.list()
        source = os.path.join(config["default"]["projectdir"], project, "source")
        conanfile = os.path.join(source, "conanfile.py")
        if not os.path.exists(os.path.join(source, "buildtools", "profiles", args.profile)):
            profile = api.profiles.get_profile([args.profile])
        else:
            profile = api.profiles.get_profile([args.profile], cwd=os.path.join(source, "buildtools", "profiles"))

        if not os.path.exists(conanfile):
            problems.append(f"Could not find {conanfile}.")
            return problems
        
        tmp = tempfile.TemporaryDirectory()

        # Iteratively discover missing pacakges by trying to construct the dependency graph.
        while True:
            # Try to construct dependency graph.
            try:
                deps_graph = api.graph.load_graph_consumer(conanfile, None, None,
                                                           None, None,
                                                           profile, profile, None,
                                                           remotes, [], False, False)
            except ConanException as e:
                # Special handling for the python_requires, since that throws an exception instead of giving a nice
                # error.
                pattern = re.compile(r"pyreq\/\d+\.\d+\.\d+@timzoet\/v\d+\.\d+\.\d+")
                pyreq_tag = pattern.search(str(e))
                if pyreq_tag:
                    # Determine URL.
                    if config.getboolean("default", "http"):
                        url = "https://github.com/TimZoet/pyreq.git"
                    else:
                        url = "git@github.com:TimZoet/pyreq.git"

                    # Clone repo and export.
                    dep_source = os.path.join(tmp.name, "pyreq")
                    subprocess.check_call(["git", "clone", url, "--depth", "1", "-b", pyreq_tag.group(0).split('/')[2],
                                           dep_source])
                    subprocess.check_call(["conan", "export", dep_source])
                    continue
                
                problems.append(f"Unexpected error when reading {conanfile}: {e}.")
                break

            # No error means all good, all packages found.
            if not deps_graph.error:
                break

            # Unexpected error or missing package from some other weirdo.
            if not isinstance(deps_graph.error, GraphMissingError) or deps_graph.error.require.ref.user != "timzoet":
                print(f"Failed to resolve dependency for {project}.")
                problems.append(f"Failed to resolve dependency {deps_graph.error.require.ref.name}.")
                break

            # Determine URL.
            if config.getboolean("default", "http"):
                url = f"https://github.com/TimZoet/{deps_graph.error.require.ref.name}.git"
            else:
                url = f"git@github.com:TimZoet/{deps_graph.error.require.ref.name}.git"

            # Clone repo and export.
            dep_source = os.path.join(tmp.name, deps_graph.error.require.ref.name)
            subprocess.check_call(["git", "clone", url, "--depth", "1", "--recurse-submodules", "-b",
                                   deps_graph.error.require.ref.channel, dep_source])
            subprocess.check_call(["conan", "export", dep_source])

        return problems

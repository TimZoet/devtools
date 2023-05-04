import argparse
import configparser
import os
import platform
import re
import subprocess
import sys
import typing

from conan.api.conan_api import ConanAPI
from conans.client.graph.graph_error import GraphMissingError
from conans.errors import ConanException
from .conanutils import ConanUtils
from .gitutils import GitUtils

known_projects = [
    "alexandria",
    "bettertest",
    "cmake-modules",
    "common",
    "cppql",
    "dot",
    "math",
    "parsertongue",
    "pyreq",
    "sol"
]

def filter_known_projects(projects):
    # Drop duplicate and unknown projects.
    return list(p for p in set(projects) if p.split("/")[0] in known_projects)

class Commands:
    @staticmethod
    def validate():
        if os.getenv("DEVTOOLS_ROOT_DIR") is None:
            raise RuntimeError("Missing DEVTOOLS_ROOT_DIR environment variable.")
        if platform.system() not in ["Windows", "Linux"]:
            raise RuntimeError(f"Unknown platform: {platform.system()}")
        if not os.path.exists(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini")):
            raise RuntimeError("Could not find INI file.")

    @staticmethod
    def packages(_):
        """
        Install required Python packages.
        """

        Commands.validate()

        pkg = ["conan>=2.0.3", "Sphinx>=6.0", "pydata-sphinx-theme", "gitpython>=3.1"]
        for p in pkg:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])
        
        # Install base Conan profiles.
        subprocess.check_call(["conan", "config", "install", "-t", "dir", "-sf", "profiles", "-tf", "profiles", os.path.join(os.path.dirname(__file__), "conan-config", "profiles")])

    @staticmethod
    def clone(args) -> typing.Iterable[str]:
        """
        Clone all known projects. Defaults to trunk branch for all projects, unless otherwise specified.
        """
        Commands.validate()

        if args.projects:
            projects = filter_known_projects(args.projects)
        else:
            projects = known_projects

        problems = []

        config = configparser.ConfigParser()
        config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))

        for p in projects:
            tag = None
            if "/" in p:
                p, tag = p.split("/")

            url = f"git@github.com:TimZoet/{p}.git"
            source = os.path.join(config["default"]["projectdir"], p, "source")
            repo = GitUtils.open_or_clone(url, source)

            if tag:
                print(f"Checking out {tag}.")
                try:
                    repo.git.checkout(tag)
                except Exception as e:
                    print(f"Failed to check out specific branch due to the following error: {e}.")
                    problems.append(f"Failed to checkout branch {tag} for {url} at {source}.")

            del repo

        return problems

    @staticmethod
    def export(args) -> typing.Iterable[str]:
        Commands.validate()

        if args.projects:
            projects = filter_known_projects(args.projects)
        else:
            projects = known_projects

        problems = []

        config = configparser.ConfigParser()
        config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))

        for p in projects:
            success, err = ConanUtils.export(config, p)
            if not success:
                problems.append(err)

        return problems

    @staticmethod
    def export_deps(args) -> typing.Iterable[str]:
        Commands.validate()

        config = configparser.ConfigParser()
        config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))

        problems = []

        project, tag = args.project, None
        if "/" in project:
            project, tag = project.split("/")

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
                    ConanUtils.export(config, f"pyreq/{pyreq_tag.group(0).split('/')[2]}")
                    continue

                problems.append(f"Unexpected error when reading {conanfile}: {e}.")
                break

            # No error means all good, all packages found.
            if not deps_graph.error:
                break

            # Unexpected error or missing package from some other weirdo.
            if not isinstance(deps_graph.error, GraphMissingError) or deps_graph.error.require.ref.user != "timzoet":
                print(f"Failed to resolve dependency for {p}.")
                problems.append(f"Failed to resolve dependency {deps_graph.error.require.ref.name}.")
                break

            # Export requirement to local cache.
            ConanUtils.export(config, f"{deps_graph.error.require.ref.name}/{deps_graph.error.require.ref.channel}")

        return problems

    @staticmethod
    def clear_cache(_):
        for p in known_projects:
            print(f"Removing {p}.")
            subprocess.check_call(["conan", "remove", "-c", f"{p}/*"])

    @staticmethod
    def install(args) -> typing.Iterable[str]:
        Commands.validate()

        config = configparser.ConfigParser()
        config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))

        problems = []

        project = args.project
        if "/" in project:
            project, _ = project.split("/")

        source = os.path.join(config["default"]["projectdir"], project, "source")
        if os.path.isabs(args.output_folder):
            target = args.output_folder
        else:
            target = os.path.join(config["default"]["projectdir"], project, args.output_folder)
        build = [f"--build={b}" for b in args.build]
        conanfile = os.path.join(source, "conanfile.py")
        if os.path.exists(os.path.join(source, "buildtools", "profiles", args.profile)):
            profile = os.path.join(source, "buildtools", "profiles", args.profile)
        else:
            profile = args.profile

        if not os.path.exists(conanfile):
            problems.append(f"Could not find {conanfile}.")
            return problems

        subprocess.check_call(["conan", "install", f"-pr:h={profile}", f"-pr:b={profile}", *build, f"-of={target}",
                               source])

        return problems

    @staticmethod
    def generate(args) -> typing.Iterable[str]:
        Commands.validate()

        problems = []

        project = args.project
        if "/" in project:
            project, _ = project.split("/")

        config = configparser.ConfigParser()
        config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))

        source = os.path.join(config["default"]["projectdir"], project, "source")
        if os.path.isabs(args.output_folder):
            target = args.output_folder
        else:
            target = os.path.join(config["default"]["projectdir"], project, args.output_folder)

        if platform.system() == "Windows":
            subprocess.check_call(["cmake", "-G", "Visual Studio 17 2022", "-A", "x64", "-T", "v143", "--toolchain",
                                   "conan_toolchain.cmake", "-S", source, "-B", target])
        else:
            problems.append("Cannot generate on any platforms other that Windows yet.")
            return problems

        return problems

if __name__ == "__main__":
    home = os.path.expanduser("~")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p_packages = subparsers.add_parser("python-packages", help="Installs required Python packages.")
    p_packages.set_defaults(func=Commands.packages)

    p_clone = subparsers.add_parser("clone", help="Clones all known or explicitly specified projects.")
    p_clone.add_argument("--projects", nargs="*", required=False, help="List of projects\
                            that are retrieved. If empty, all known projects are retrieved. To clone specific projects\
                            and specific tags, use 'project/tag'.")
    p_clone.set_defaults(func=Commands.clone)

    p_export = subparsers.add_parser("export", help="Exports packages to the local Conan cache.")
    p_export.add_argument("--projects", nargs="*", required=False, help="List of projects that are exported to the\
                          Conan cache. If empty, all known projects are exported. To export specific projects and\
                          specific tags, use 'project/tag'.")
    p_export.set_defaults(func=Commands.export)

    p_export_deps = subparsers.add_parser("export-deps", help="Automatically resolves all required packages for a\
                                          single project and exports them to the local Conan cache.")
    p_export_deps.add_argument("--project", dest="project", required=True, help="Project name.  To specify a tag, use\
                               'project/tag'.")
    p_export_deps.add_argument("--profile", dest="profile", required=True, help="Name of profile. Can be a profile\
                               stored in the Conan cache, or in the current projects' buildtools/profiles folder. The\
                               latter takes precedence.")
    p_export_deps.set_defaults(func=Commands.export_deps)

    p_clear_cache = subparsers.add_parser("clear-cache", help="Removes all known projects from the local Conan cache.")
    p_clear_cache.set_defaults(func=Commands.clear_cache)

    p_install = subparsers.add_parser("conan-install", help="Runs the `conan install` command for a single project.")
    p_install.add_argument("--project", dest="project", required=True, help="Project name.")
    p_install.add_argument("--profile", dest="profile", required=True, help="Name of profile. Can be a profile stored\
                           in the Conan cache, or in the current projects' buildtools/profiles folder. The latter takes\
                           precedence.")
    p_install.add_argument("--build", nargs="*", dest="build", required=False, default=["missing:*"], help="List of\
                           values passed on directly to the --build argument of the conan install command. Defaults to\
                           'missing:*'.")
    p_install.add_argument("--output-folder", "--of", "-of", dest="output_folder", required=False, default="build",
                           help="Output folder, passed to the -of argument of the conan install command. If relative,\
                           it is joined with the current projects' root folder (i.e. next to the source folder.")
    p_install.set_defaults(func=Commands.install)

    p_generate = subparsers.add_parser("cmake-generate", help="Runs the cmake generate command for a single project.")
    p_generate.add_argument("--project", dest="project", required=True, help="Project name.")
    p_generate.add_argument("--output-folder", "--of", "-of", dest="output_folder", required=False, default="build",
                            help="Output folder, passed to the -of argument of the conan install command. If relative,\
                            it is joined with the current projects' root folder (i.e. next to the source folder.")
    p_generate.set_defaults(func=Commands.generate)

    a = parser.parse_args()

    try:
        problems = a.func(a)
    except Exception as ee:
        print(f"Failed to run command. Unexpected error: {ee}")
        sys.exit(1)

    if problems:
        print("")
        print("Failed to run command. Known problems:")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)

    print("devtools ran successfully.")

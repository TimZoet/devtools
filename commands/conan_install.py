import argparse
import os
import subprocess
import typing

from utils import get_config, known_projects, get_arg_project

class ConanInstallCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("conan-install", help="Runs the `conan install` command for a single project.")
        p.add_argument("--project", dest="project", help="Project name. If not set, will try to derive current\
                           project from working directory.")
        p.add_argument("--profile", dest="profile", required=True, help="Name of profile. Can be a profile stored\
                           in the Conan cache, or in the current projects' buildtools/profiles folder. The latter takes\
                           precedence.")
        p.add_argument("--build", nargs="*", dest="build", required=False, default=["missing:*"], help="List of\
                           values passed on directly to the --build argument of the conan install command. Defaults to\
                           'missing:*'.")
        p.add_argument("--output-folder", "--of", "-of", dest="output_folder", required=False, default="build",
                           help="Output folder, passed to the -of argument of the conan install command. If relative,\
                           it is joined with the current projects' root folder (i.e. next to the source folder.")
        p.set_defaults(func=ConanInstallCommand.run)
    
    @staticmethod
    def run(args) -> typing.Iterable[str]:
        config = get_config()

        problems = []

        project = args.project
        if project is None:
            project = os.path.basename(os.path.normpath(os.getcwd()))
        if "/" in project:
            project, _ = project.split("/")
        if project not in known_projects:
            problems.append(f"Unknown project {project}.")
            return problems

        known, project, _ = get_arg_project(args)
        if not known:
            problems.append(f"Unknown project {project}.")
            return problems

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

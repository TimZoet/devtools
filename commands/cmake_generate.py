import argparse
import os
import platform
import subprocess
import typing

from utils import get_config, get_arg_project

class CmakeGenerateCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("cmake-generate", help="Runs the cmake generate command for a single project.")
        p.add_argument("--project", dest="project", help="Project name. If not set, will try to derive current\
                        project from working directory.")
        p.add_argument("--output-folder", "--of", "-of", dest="output_folder", required=False, default="build",
                        help="Output folder, passed to the -of argument of the conan install command. If relative,\
                        it is joined with the current projects' root folder (i.e. next to the source folder.")
        p.set_defaults(func=CmakeGenerateCommand.run)
    
    @staticmethod
    def run(args) -> typing.Iterable[str]:
        problems = []

        known, project, _ = get_arg_project(args)
        if not known:
            problems.append(f"Unknown project {project}.")
            return problems

        config = get_config()

        source = os.path.join(config["default"]["projectdir"], project, "source")
        if os.path.isabs(args.output_folder):
            target = args.output_folder
        else:
            target = os.path.join(config["default"]["projectdir"], project, args.output_folder)

        if platform.system() == "Windows":
            subprocess.check_call(["cmake", "-G", "Visual Studio 17 2022", "-A", "x64", "-T", "v143", "--toolchain",
                                   "conan_toolchain.cmake", "-S", source, "-B", target])
        else:
            problems.append("Cannot generate on any platforms other than Windows yet.")
            return problems

        return problems

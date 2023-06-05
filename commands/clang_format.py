import argparse
import os
import platform
import subprocess
import typing

from utils import get_config, get_arg_project

def get_clang_format_path() -> str:
    return os.path.join(os.getenv("VCINSTALLDIR"), "Tools/Llvm/x64/bin/clang-format.exe")

class ClangFormatCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("clang-format", help="Runs clang-format on a single project.")
        p.add_argument("--project", dest="project", help="Project name. If not set, will try to derive current\
                        project from working directory.")
        p.set_defaults(func=ClangFormatCommand.run)

    @staticmethod
    def run(args) -> typing.Iterable[str]:
        problems = []
        if platform.system() != "Windows":
            problems.append("clang-format is currently only supported on Windows.")

        known, project, _ = get_arg_project(args)
        if not known:
            problems.append(f"Unknown project {project}.")
            return problems

        cf = get_clang_format_path()

        def format_dir(folder: str) -> None:
            for file in os.listdir(folder):
                item = os.path.join(folder, file)
                if os.path.isfile(item) and os.path.splitext(item)[1] in [".h", ".cpp"]:
                    subprocess.check_call([cf, "-i", item])
                elif os.path.isdir(item):
                    format_dir(item)

        config = get_config()
        source = os.path.join(config["default"]["projectdir"], project, "source")
        format_dir(source)

        return problems

import argparse
import os
import platform
import sys

from commands.clang_format import ClangFormatCommand
from commands.clear_cache import ClearCacheCommand
from commands.clone import CloneCommand
from commands.cmake_generate import CmakeGenerateCommand
from commands.conan_install import ConanInstallCommand
from commands.export import ExportCommand
from commands.export_deps import ExportDepsCommand
from commands.python_packages import PythonPackagesCommand

def validate():
    if os.getenv("DEVTOOLS_ROOT_DIR") is None:
        raise RuntimeError("Missing DEVTOOLS_ROOT_DIR environment variable.")
    if platform.system() not in ["Windows", "Linux"]:
        raise RuntimeError(f"Unknown platform: {platform.system()}")
    if not os.path.exists(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini")):
        raise RuntimeError("Could not find INI file.")

if __name__ == "__main__":
    validate()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    ClangFormatCommand.setup(subparsers)
    ClearCacheCommand.setup(subparsers)
    CloneCommand.setup(subparsers)
    ExportCommand.setup(subparsers)
    ExportDepsCommand.setup(subparsers)
    CmakeGenerateCommand.setup(subparsers)
    ConanInstallCommand.setup(subparsers)
    PythonPackagesCommand.setup(subparsers)

    a = parser.parse_args()

    try:
        problems = a.func(a)
    except Exception as ee:
        print("=====================================================")
        print(f"Failed to run devtools command. Unexpected error: {ee}")
        sys.exit(1)

    if problems:
        print("")
        print("Failed to run command. Known problems:")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)

    print("=====================================================")
    print("devtools ran successfully.")

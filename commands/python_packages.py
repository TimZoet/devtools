import argparse
import os
import subprocess
import sys
import typing

class PythonPackagesCommand:
    @staticmethod
    def setup(parser: argparse.ArgumentParser):
        p = parser.add_parser("python-packages", help="Installs required Python packages.")
        p.set_defaults(func=PythonPackagesCommand.run)

    @staticmethod
    def run(args) -> typing.Iterable[str]:
        pkg = ["conan>=2.0.3", "Sphinx>=6.0", "pydata-sphinx-theme", "gitpython>=3.1"]
        for p in pkg:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

        # Install base Conan profiles.
        subprocess.check_call(["conan", "config", "install", "-t", "dir", "-sf", "profiles", "-tf", "profiles", 
                               os.path.join(os.path.dirname(__file__), "conan-config", "profiles")])

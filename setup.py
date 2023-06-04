import argparse
import configparser
import os
import platform
import sys

def setup(args):
    if not os.path.isabs(args.dir):
        raise RuntimeError(f"Root directory {args.dir} is not an absolute path.")

    if platform.system() == "Windows":
        filename = os.path.join(args.dir, "startup.bat")
        source = f"""
@echo off
set PATH={os.path.join(sys.path[0], "windows")};%PATH%
set DEVTOOLS_ROOT_DIR={args.dir}
set CONAN_HOME={args.conan}
{args.pyenv}\\Scripts\\activate.bat
@echo on
"""
    else:
        filename = os.path.join(args.dir, "startup")
        source = f"""
export PATH={os.path.join(sys.path[0], "linux")}:$PATH
export DEVTOOLS_ROOT_DIR={args.dir}
export CONAN_HOME={args.conan}
source ~/dev/pyenv/bin/activate
alias python=python3
alias pip=pip3
"""
    print(f"Writing startup file {filename}.")
    if os.path.exists(filename):
        print("File already exists, overwriting.")
    with open(filename, encoding="UTF8", mode="w") as f:
        f.write(source)

    filename = os.path.join(args.dir, "devtools.ini")
    print(f"Writing INI file {filename}.")
    with open(filename, encoding="UTF8", mode="w") as f:
        config = configparser.ConfigParser()
        config["default"] = {
            "projectdir": args.projectdir if os.path.isabs(args.projectdir) else os.path.join(args.dir, args.projectdir),
            "http": str(args.http)
        }
        config.write(f)

    print("Setup done.")

if __name__ == "__main__":
    home = os.path.expanduser("~")

    parser = argparse.ArgumentParser()

    parser.add_argument("--dir", dest="dir", required=False, default=os.path.join(home, "dev"),
                        help="Root directory in which all the magic happens. Defaults to ~/dev.")
    parser.add_argument("--pyenv", dest="pyenv", required=False, default=os.path.join(home, "dev", "pyenv"),
                        help="Optional path to Python virtual environment. Defaults to ~/dev/pyenv.")
    parser.add_argument("--conan", dest="conan", required=False, default=os.path.join(home, "dev", ".conan"),
                        help="Optional path to Conan home directory. Defaults to ~/dev/.conan.")
    parser.add_argument("--projectdir", dest="projectdir", required=False, default="projects", help="Directory in which\
                        repositories are stored. If relative, it is joined with the root directory.")
    parser.add_argument("--http", "--https", dest="http", action="store_true", help="Use HTTP(S) to clone repositories.\
                        Useful if you do not have SSH configured.")
    parser.set_defaults(func=setup)

    a = parser.parse_args()

    try:
        a.func(a)
    except Exception as e:
        import traceback
        print(f"Failed to run command. Unexpected error: {e}")
        traceback.print_exception(e)
        sys.exit(1)

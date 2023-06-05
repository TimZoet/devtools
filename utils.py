import configparser
import os
import pathlib
import typing

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

def get_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv("DEVTOOLS_ROOT_DIR"), "devtools.ini"))
    return config

def get_arg_project(args) -> typing.Tuple[bool, typing.Optional[str], typing.Optional[str]]:
    """Retrieve an explicit project name from the parser arguments, or try to derive from the current working
    directory.

    Args:
        args: Parser arguments.

    Returns:
        typing.Tuple[bool, typing.Optional[str], typing.Optional[str]]: success, project, tag
    """
    project = args.project
    tag = None

    # If no explicit project was given, try to derive from the current directory. This is done by subtracting the
    # projectdir from the front, and then taking the first directory name. E.g.:
    # projectdir = /path/to/dev/projects
    # currentdir = /path/to/dev/projects/<project>/whatevs/something
    #                                    ^^^^^^^^^
    if project is None:
        config = get_config()
        projectdir = os.path.normpath(config["default"]["projectdir"])
        currentdir = os.path.normpath(os.getcwd())
        if os.path.commonprefix([projectdir, currentdir]) == projectdir:
            project = pathlib.Path(os.path.relpath(currentdir, projectdir)).parts[0]

    elif "/" in project:
        project, tag = project.split("/")

    if project not in known_projects:
        return False, project, tag

    return True, project, tag

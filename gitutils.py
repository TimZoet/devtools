import configparser
import os
import typing

import git

class RestorableCommit:
    def __init__(self, repo: git.Repo) -> None:
        self.repo = repo
        self.detached = self.repo.head.is_detached
        self.commit = self.repo.head.object.hexsha if self.detached else None
        self.branch = self.repo.active_branch.name if not self.detached else None

    def restore(self):
        if self.detached:
            print(f"Restoring to commit {self.commit}.")
            self.repo.git.checkout(self.commit)
        else:
            print(f"Restoring to branch {self.branch}.")
            self.repo.git.checkout(self.branch)

class GitUtils:
    @staticmethod
    def clone_url(url, target) -> git.Repo:
        print(f"Cloning repository from {url} to {target}.")
        repo = git.Repo.clone_from(url=url, to_path=target)

        # Retrieve submodules.
        for submodule in repo.submodules:
            submodule.update(init=True)

        return repo
    
    @staticmethod
    def open_or_clone_url(url, target) -> git.Repo:
        if os.path.exists(os.path.join(target, ".git")):
            print(f"Opening existing repository at {target}.")
            repo = git.Repo(target)
        else:
            print(f"Cloning repository from {url} to {target}.")
            repo = git.Repo.clone_from(url=url, to_path=target)

            # Retrieve submodules.
            for submodule in repo.submodules:
                submodule.update(init=True)

        return repo
    
    @staticmethod
    def open_or_clone_project(project: str, target: str, config: configparser.ConfigParser) -> typing.Tuple[git.Repo, typing.Iterable[str]]:
        problems = []

        # Split into project name and optional tag.
        tag = None
        if "/" in project:
            project, tag = project.split("/")

        # Determine URL.
        if config.getboolean("default", "http"):
            url = f"https://github.com/TimZoet/{project}.git"
        else:
            url = f"git@github.com:TimZoet/{project}.git"

        # Determine source directory.
        # source = os.path.join(config["default"]["projectdir"], project, "source")

        repo = GitUtils.open_or_clone_url(url, target)

        if tag:
            print(f"Checking out {tag}.")
            try:
                repo.git.checkout(tag)
            except Exception as e:
                print(f"Failed to check out specific branch due to the following error: {e}.")
                problems.append(f"Failed to checkout branch {tag} for {url} at {target}.")
                repo = None

        return repo, problems

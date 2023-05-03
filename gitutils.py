import os

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
    def open_or_clone(url, target) -> git.Repo:
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
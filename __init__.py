import configparser
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

class Conan:
    @staticmethod
    def export(config: configparser.ConfigParser, project: str) -> typing.Tuple[bool, typing.Optional[str]]:
        """Export a project to the local Conan cache. By default the current state of the repository is exported. When a
        branch/tag is specified, an attempt is made to perform a checkout before doing the export. The repository is
        restored to its original state afterwards.

        Args:
            config (configparser.ConfigParser): Config.
            project (str): Project name and optional branch/tag to export.

        Returns:
            typing.Tuple[bool, typing.Optional[str]]: Boolean indicating success and an optional error message on
            failure.
        """
        # TODO: Introduce an option to stash and restore changes that might prevent a checkout.
        
        tag = None
        if ":" in project:
            project, tag = project.split(":")

        source = os.path.join(config["default"]["projectdir"], project, "source")
        try:
            repo = git.Repo(source)
            commit = RestorableCommit(repo)
        except Exception as e:
            print(f"Failed to open repository due to the following error: {e}.")
            return False, f"Failed to open repository {project} at {source}."

        if tag:
            print(f"Checking out {tag}.")
            try:
                repo.git.checkout(tag)
            except Exception as e:
                print(f"Failed to check out specific branch due to the following error: {e}.")
                return False, f"Failed to checkout branch {tag} at {source}. Export of {project} did not succeed."
        
        try:
            subprocess.check_call(["conan", "export", source])
        finally:
            commit.restore()

        del commit
        del repo
        return True, None
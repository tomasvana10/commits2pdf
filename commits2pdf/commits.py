from __future__ import annotations

from datetime import datetime
from os import path
from shutil import rmtree
from typing import Dict, List, Union

from git import Commit as GitCommit
from git import (
    GitCommandError,
    Head,
    InvalidGitRepositoryError,
    NoSuchPathError,
    Repo,
)

from .constants import (
    CLONING_REPO_INFO,
    CODING,
    DETACHED_BRANCH_ERROR,
    FILTER_INFO,
    GATHERED_COMMITS_INFO,
    INVALID_GIT_REPO_ERROR,
    MUST_RECLONE_ERROR,
    N_COMMITS_INFO,
    N_COMMITS_WARNING,
    NONEXISTING_BRANCH_WARNING,
    NONEXISTING_OR_INVALID_REPO_ERROR,
    NONEXISTING_REPO_ERROR,
    REPO_ALREADY_EXISTS_WARNING,
    ZERO_COMMITS_WARNING,
)
from .logger import logger


class Commits(object):
    """Represents a filtered set of commits along with filter information."""

    def __init__(self, **kwargs) -> None:
        """Save filter and repo information from kwargs."""
        self.err_flag: bool = False  # Detected in ``cli.py`` to stop execution

        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

        self.r: Repo = self._get_repo()
        if isinstance(self.r, Repo):  # Repo was successfully found, continue
            self._init_repo_data()
        elif self.r == "DELTREE":  # Perform buffered deletion due to errors in
                                   # ``_get_repo``.
            rmtree(self.rpath, ignore_errors=True)
            self.err_flag = True
        elif not self.r:  # ``_get_repo`` returned NoneType, so the repo could
                          # not be accessed
            self.err_flag = True

    def _init_repo_data(self) -> None:
        """Find the repo name (preferrably from the remote), then
        sequentially build the filtered commits from the commits of the
        repo.
        """
        if len(self.r.remotes) > 0:  # Use remote name
            self.rname: str = self.r.remotes.origin.url.split(".git")[0].split(
                "/"
            )[-1]
        else:  # No remote exists, just get the name of the directory
            self.rname: str = path.basename(
                self.r.working_tree_dir.split("/")[-1]
            )

        self.raw_commits: List[Repo.commit] = self._gather_commits()
        self.commit_objects: List[Commit] = self._instantiate_commits()
        self.filtered_commits: List[Commit] = self._filter_commits()
        if len(self.filtered_commits) == 0:
            logger.warning(ZERO_COMMITS_WARNING)

    def _retry_clone(self, e) -> Union[Repo, str, None]:
        """Reattempt cloning if possible and update ``self.branch`` accordingly."""
        rmtree(self.rpath, ignore_errors=True)
        if (
            "remote branch" in str(e).casefold()
        ):  # User entered invalid branch, so clone repo without specifying a 
            # branch argument
            r: Repo = Repo.clone_from(self.url, self.rpath, no_checkout=True)
            try:
                b: Head = r.active_branch
            except TypeError:  # Repo branch is detached
                return logger.error(DETACHED_BRANCH_ERROR.format(self.branch))

            logger.warning(NONEXISTING_BRANCH_WARNING.format(self.branch, b))
            self.branch = b
            return r

        else:  # Some other error occurred
            logger.error(NONEXISTING_OR_INVALID_REPO_ERROR.format(self.url))
            return "DELTREE"

    def _validate_branch(self, r: Repo) -> Union[bool, None]:
        """Ensure that ``self.branch`` exists. If not, attempt to set it to the
        repo's active branch.
        """
        if self.branch == str(r.active_branch):
            return True

        try:  # The branch they want does not exist, so access the active branch
            b: Head = r.active_branch
        except TypeError:
            return logger.error(DETACHED_BRANCH_ERROR.format(self.branch))

        logger.warning(NONEXISTING_BRANCH_WARNING.format(self.branch, b))
        self.branch: Head = b  # Update the branch to the repo's active branch
        return True

    def _clone_repo(self) -> Union[Repo, str, None]:
        """Attempt to clone a repo's .git directory."""
        logger.info(CLONING_REPO_INFO)
        try:
            r: Repo = Repo.clone_from(
                self.url,
                self.rpath,
                branch=self.branch,
                no_checkout=True,
            )
            return r
        except GitCommandError as e:
            return self._retry_clone(e)

    def _get_repo(self) -> Union[Repo, str, None]:
        """Access a repo, or clone it and then access it, and update
        ``self.branch`` if necessary. Complete with extensive error handling,
        ensuring a high chance of the user's requests being processed.
        """
        if self.url:  # User wants to clone a repo
            if path.exists(self.rpath) and path.isdir(self.rpath):  # Repo may
                # exist
                if path.exists(path.join(self.rpath, ".git")):  # .git exists
                    logger.warn(REPO_ALREADY_EXISTS_WARNING)
                    try:
                        r: Repo = Repo(self.rpath)  # Attempt to access repo
                    except NoSuchPathError:
                        return logger.error(NONEXISTING_REPO_ERROR)

                    return r if self._validate_branch(r) else None

                else:  # .git does not exist, delete the existing folder and
                       # clone the repo
                    rmtree(self.rpath, ignore_errors=True)
                    return self._clone_repo()

            else:  # Repo does not exist, just clone it
                return self._clone_repo()

        else:  # Just access the repo normally
            try:
                r: Repo = Repo(self.rpath)
                return r if self._validate_branch(r) else None

            except InvalidGitRepositoryError:
                return logger.error(INVALID_GIT_REPO_ERROR.format(self.rpath))
            except NoSuchPathError:
                return logger.error(NONEXISTING_REPO_ERROR)

    def _gather_commits(self) -> List[GitCommit]:
        """Find all the commits that match the user's since, until and branch
        specifications.
        """
        try:
            commits: List[GitCommit] = list(
                self.r.iter_commits(
                    since=self.start_date,
                    until=self.end_date,
                    rev=self.branch,
                )
            )
        except Exception:
            logger.error(MUST_RECLONE_ERROR)
            self.err_flag = True
            exit(1)

        logger.info(GATHERED_COMMITS_INFO.format(len(commits)))

        return commits

    def _instantiate_commits(self) -> List[Dict[str, str]]:
        """Instantiate all the filtered ``Repo.commit`` objects into my own
        simple class that inherits from a dictionary.
        """
        commit_objects = []
        for commit in self.raw_commits:
            commit_objects.append(
                Commit(self.owner, self.rname, self.branch, commit)
            )

        return commit_objects

    def _filter_commits(self) -> List[Commit]:
        """Process the Commit objects based on user-specified criteria such as
        authors and queries.
        """
        filtered_commits: List[Commit] = self.commit_objects
        if self.include:
            filtered_commits: List[Commit] = [
                commit
                for commit in self.commit_objects
                for q in self.include
                if q.casefold() in commit["description"].casefold()
                or q.casefold() in commit["title"].casefold()
            ]
            logger.info(
                FILTER_INFO.format(
                    len(filtered_commits),
                    len(self.commit_objects),
                    "include queries",
                )
            )
        if self.exclude:
            prior_len: int = len(filtered_commits)
            filtered_commits: List[Commit] = [
                commit
                for commit in filtered_commits
                for q in self.exclude
                if q.casefold() not in commit["description"].casefold()
                and q.casefold() not in commit["title"].casefold()
            ]
            logger.info(
                FILTER_INFO.format(
                    len(filtered_commits), prior_len, "exclude queries"
                )
            )
        if self.authors:
            prior_len: int = len(filtered_commits)
            filtered_commits: List[Commit] = [
                commit
                for commit in filtered_commits
                if commit["author_email"] in self.authors
            ]
            logger.info(
                FILTER_INFO.format(
                    len(filtered_commits), prior_len, "author email"
                )
            )

        if self.newest_n_commits:
            if not self.newest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[: self.newest_n_commits]
                logger.info(
                    N_COMMITS_INFO.format("newest", self.newest_n_commits)
                )
            else:
                logger.warn(
                    N_COMMITS_WARNING.format(
                        "Newest", self.newest_n_commits, len(filtered_commits)
                    )
                )
        elif self.oldest_n_commits:
            if not self.oldest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[-self.oldest_n_commits :]
                logger.info(
                    N_COMMITS_INFO.format(
                        "oldest", self.oldest_n_commits, len(filtered_commits)
                    )
                )
            else:
                logger.warn(
                    N_COMMITS_WARNING.format(
                        "Oldest", self.oldest_n_commits, len(filtered_commits)
                    )
                )

        step: int = -1 if not self.reverse else 1
        filtered_commits = filtered_commits[::step]

        return filtered_commits


class Commit(dict):
    """A simple way of representing a commit as a dictionary."""

    def __init__(
        self, owner: str, rname: str, branch: str, commit: Repo.commit
    ) -> None:
        """Assign commit data to the instance."""
        self["rname"] = rname
        self["branch"] = branch
        self["author_name"] = commit.author
        self["author_email"] = commit.author.email
        self["date"] = datetime.fromtimestamp(commit.committed_date)
        self["hexsha_short"] = commit.hexsha[:7]
        self["hexsha_long"] = commit.hexsha
        self["diff_url"] = (
            f"https://github.com/{owner}/{rname}/commit/{commit.hexsha}"
        )

        self["info"] = (
            f"{self['hexsha_short']} | "
            f"By {self['author_name']} ({self['author_email']}) | "
            f"At {self['date'].strftime('%d/%m/%Y')}"
        )
        self["info"] = Commit._code(self["info"])

        # Extract the message from the title
        msg = commit.message.split("\n")
        self["title"] = Commit._code(msg[0])
        self["description"] = (
            Commit._code("\n".join(msg[1:])) if len(msg) > 1 else ""
        )

    @staticmethod
    def _code(text: str, coding: str = CODING) -> str:
        return text.encode(CODING, "replace").decode(CODING)

    def __str__(self) -> str:
        """View the commit in the terminal."""
        return (
            "=============================\n"
            f"Repository: {self['rname']}\n"
            f"{self['info']}\n"
            f"{self['title']}\n"
            f"{self['description']}\n"
            f"View diff: {self['diff_url']}\n"
            "=============================\n"
        )

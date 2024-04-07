from os import path, listdir
from datetime import datetime
from shutil import rmtree
from typing import List, Union, Dict

from git import Repo, GitCommandError, InvalidGitRepositoryError

from .logger import logger
from .constants import (
    REPO_ALREADY_EXISTS_WARNING, DETACHED_BRANCH_ERROR, 
    BRANCH_ALREADY_EXISTS_WARNING, INVALID_REPO_ERROR, INVALID_REPO_ERROR_2,
    FILTER_INFO, N_COMMITS_INFO, N_COMMITS_WARN, GATHERED_COMMITS_INFO
)


class Commits(object):
    """Represents a filtered set of commits along with filter information."""
    def __init__(self, **kwargs) -> None:
        """Save filter and repo information from kwargs."""
        self.err_flag: bool = False # Detected in ``cli.py`` to stop execution
        
        self.rpath: str = kwargs["rpath"]
        self.owner: str = kwargs["owner"]
        self.url: Union[str, None] = kwargs["url"]
        self.branch: Union[str, None] = kwargs["branch"]
        self.authors: Union[List[str], None] = kwargs["authors"]
        self.start_date: Union[datetime, None] = kwargs["start_date"]
        self.end_date: Union[datetime, None] = kwargs["end_date"]
        self.reverse: bool = kwargs["reverse"]
        self.newest_n_commits: int = kwargs["newest_n_commits"]
        self.oldest_n_commits: int= kwargs["oldest_n_commits"]
        self.queries_any: List[str] = kwargs["queries_any"]
        self.queries_all: List[str] = kwargs["queries_all"]

        self.r: Repo = self.get_repo()  
        if isinstance(self.r, Repo): # Repo was successfully found, continue
            self.init_repo_data()
        elif self.r == "deltree": # Buffered deletion due to errors in
                                  # ``get_repo``.
            rmtree(self.rpath, ignore_errors=True)
            self.err_flag = True
        elif not self.r: # ``get_repo`` returned nothing, so the repo could not
                         # be accessed
            self.err_flag = True
            
    def init_repo_data(self) -> None:
        """Find the repo name (preferrably from the remote), then sequentially
        build the filtered commits from the commits of the repo.
        """
        if len(self.r.remotes) > 0: # Use remote name
            self.rname = self.r.remotes.origin.url.split(".git")[0].split("/")[-1]
        else: # No remote exists, just get the name of the directory
            self.rname = path.basename(self.r.working_tree_dir.split("/")[-1])
            
        self.raw_commits: list[Repo.commit] = self.gather_commits()
        self.commit_objects: list[Commit] = self.instantiate_commits()
        self.filtered_commits: list[Commit] = self.filter_commits()

    def get_repo(self) -> Union[Repo, str, None]: 
        """Access a repo, or clone it and then access it. Complete with extensive
        error handling, ensuring a high chance of the user's requests being
        adequately processed.
        """
        if self.url: # User wants to clone a repo
            if path.exists(self.rpath) and path.isdir(self.rpath): # Repo may exist
                if path.exists(path.join(self.rpath, ".git")):  # .git exists
                    logger.warn(REPO_ALREADY_EXISTS_WARNING)
                    r = Repo(self.rpath) # Attempt to access repo
                    if self.branch: # User is looking for specific branch
                        try:
                            b = r.active_branch
                        except TypeError: # Branch is detached
                            return logger.error(
                                DETACHED_BRANCH_ERROR.format(self.branch))
                        if not str(b) == str(self.branch): # Branch of existing 
                                                           # repo is not the 
                                                           # branch the user wants
                            logger.warning(
                                BRANCH_ALREADY_EXISTS_WARNING.format(self.branch, 
                                                                     b))
                            self.branch = b # Update the branch to the repo's 
                                            # active branch
                    return r # Repo was accessed with no problems

                else: # .git does not exist, delete the existing folder and 
                      # clone the repo
                    rmtree(self.rpath, ignore_errors=True)
                    try:
                        r = Repo.clone_from(self.url, self.rpath, 
                                            branch=self.branch, no_checkout=True)
                    except GitCommandError as e:
                        if "remote branch" in str(e).casefold(): # User entered 
                                                                 # invalid branch
                            r = Repo.clone_from(self.url, self.rpath, 
                                                no_checkout=True)
                            try:
                                b = r.active_branch
                            except TypeError:
                                return logger.error(
                                    DETACHED_BRANCH_ERROR.format(self.branch))
                            logger.warning(
                                BRANCH_ALREADY_EXISTS_WARNING.format(self.branch, 
                                                                     b))
                            self.branch = b # Update the branch to the repo's 
                                            # active branch
                        else: # Some other error occurred
                            logger.error(INVALID_REPO_ERROR.format(self.url))
                            return "deltree"

            else:  # Repo does not exist, just clone it
                try:
                    r = Repo.clone_from(self.url, self.rpath, 
                                        branch=self.branch, no_checkout=True)
                except GitCommandError as e:
                    if "remote branch" in str(e).casefold():
                        r = Repo.clone_from(self.url, self.rpath, 
                                            no_checkout=True)
                        try:
                            b = r.active_branch
                        except TypeError:
                            return logger.error(
                                DETACHED_BRANCH_ERROR.format(self.branch))
                        logger.warning(
                            BRANCH_ALREADY_EXISTS_WARNING.format(self.branch, 
                                                                 b))
                        self.branch = b
                    else: # Some other error occurred
                        logger.error(INVALID_REPO_ERROR.format(self.url))
                        return "deltree"

        else: # Just access the repo normally
            try:
                r = Repo(self.rpath)
                if self.branch:
                    try:
                        b = r.active_branch
                    except TypeError:
                        return logger.error(
                            DETACHED_BRANCH_ERROR.format(self.branch))
                    if not str(b) == str(self.branch):  # Branch of repo is not 
                                                        # the branch the user wants
                        logger.warning(
                            BRANCH_ALREADY_EXISTS_WARNING.format(self.branch, 
                                                                 b))
                        self.branch = b  # Update the branch to the repo's 
                                         # active branch

            except InvalidGitRepositoryError:
                return logger.error(INVALID_REPO_ERROR_2)

        return r

    def gather_commits(self) -> List[Repo.commit]:
        """Find all the commits that match the user's since, until and branch
        specifications.
        """
        commits = list(
            self.r.iter_commits( # If any of the params are NoneType, no prob!
                since=self.start_date,
                until=self.end_date,
                rev=self.branch,
            )
        )
        logger.info(GATHERED_COMMITS_INFO.format(len(commits)))
        
        return commits
    
    def instantiate_commits(self) -> List[Dict[str, str]]: # Can't use ``Commit`` yet bruh
        """Instantiate all the filtered ``Repo.commit`` objects into my own
        simple class that inherits from a dictionary.
        """
        commit_objects = []
        for commit in self.raw_commits:
            commit_objects.append(Commit(self.owner, self.rname, self.branch, 
                                         commit))

        return commit_objects

    def filter_commits(self) -> List[dict]:
        """Process the Commit objects based on user-specified criteria such as
        authors and queries. 
        """
        filtered_commits = self.commit_objects
        if self.queries_any or self.queries_all:
            queries, query_func = (self.queries_any, any) if self.queries_any \
                                  else (self.queries_all, all)
            filtered_commits = [commit for commit in self.commit_objects \
                                if query_func(q in commit["description"] \
                                or q in commit["title"] for q in queries)]        
            logger.info(FILTER_INFO.format(len(filtered_commits), 
                                           len(self.commit_objects), "query"))
        if self.authors:
            prior_len = len(filtered_commits)
            filtered_commits = [commit for commit in filtered_commits \
                                if commit["author_email"] in self.authors]
            logger.info(FILTER_INFO.format(len(filtered_commits), prior_len, 
                                           "author_email"))
            
        if self.newest_n_commits:
            if not self.newest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[:self.newest_n_commits]
                logger.info(N_COMMITS_INFO.format("newest", 
                                                  self.newest_n_commits))
            else:
                logger.warn(N_COMMITS_WARN.format("Newest", 
                                                  self.newest_n_commits,
                                                  len(filtered_commits)))
        elif self.oldest_n_commits:
            if not self.oldest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[-self.oldest_n_commits:]
                logger.info(N_COMMITS_INFO.format("oldest", 
                                                  self.oldest_n_commits,
                                                  len(filtered_commits)))
            else: 
                logger.warn(N_COMMITS_WARN("Oldest", self.oldest_n_commits))

        step = -1 if not self.reverse else 1
        filtered_commits = filtered_commits[::step] 
        
        return filtered_commits

class Commit(dict):
    """A simple way of representing a commit as a dictionary."""
    def __init__(self, owner, rname, branch, commit: Repo.commit):
        """Assign commit data to the instance."""
        self["rname"] = rname 
        self["branch"] = branch
        self["author_name"] = commit.author
        self["author_email"] = commit.author.email
        self["date"] = datetime.fromtimestamp(commit.committed_date)
        self["hexsha_short"] = commit.hexsha[:7]
        self["hexsha_long"] = commit.hexsha
        self["diff_url"] = f"https://github.com/{owner}/{rname}/commit/{commit.hexsha}"

        self["info"] = f"{self['hexsha_short']} | Branch: {self['branch']} | " \
                       f"By {self['author_name']} ({self['author_email']}) | " \
                       f"At {self['date'].strftime('%Y-%m-%d')}"
         
        # Extract the message from the title
        msg = commit.message.split("\n")
        self["title"] = msg[0]
        if len(msg) > 1:
            self["description"] = "\n".join(msg[1:])
        else:
            self["description"] = ""
    
    def __str__(self): 
        """View the commit in the terminal."""
        return \
            "=============================\n" \
            f"Repository: {self['rname']}\n" \
            f"{self['info']}\n" \
            f"{self['title']}\n" \
            f"{self['description']}\n" \
            f"View diff: {self['diff_url']}\n" \
            "=============================\n"
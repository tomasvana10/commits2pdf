from os import path, listdir
from datetime import datetime
from shutil import rmtree

from git import Repo, GitCommandError, InvalidGitRepositoryError

from .logger import logger

class Commits(object):
    def __init__(self, **kwargs):
        self.err_flag = False
        
        self.rpath: str = kwargs["rpath"]
        self.owner: str = kwargs["owner"]
        self.url: str = kwargs["url"]
        self.branch: str = kwargs["branch"]
        self.authors: list[str] = kwargs["authors"]
        self.start_date = kwargs["start_date"]
        self.end_date = kwargs["end_date"]
        self.reverse = kwargs["reverse"]
        self.newest_n_commits, self.oldest_n_commits = kwargs["newest_n_commits"], \
                                                       kwargs["oldest_n_commits"]
        self.queries_any, self.queries_all = kwargs["queries_any"], \
                                             kwargs["queries_all"]

        self.r = self.get_repo()  
        if isinstance(self.r, Repo):
            self.init_repo_data()
        elif self.r == "deltree":
            rmtree(self.rpath, ignore_errors=True)
            self.err_flag = True
        elif not self.r:
            self.err_flag = True
            
    def init_repo_data(self):
        if len(self.r.remotes) > 0:
            self.rname = self.r.remotes.origin.url.split(".git")[0].split("/")[-1]
        else:
            self.rname = path.basename(self.r.working_tree_dir.split("/")[-1])
        self.raw_commits: list[Repo.commit] = self.gather_commits()
        self.commit_objects: list[Commit] = self.instantiate_commits()
        self.filtered_commits: list[Commit] = self.filter_commits()

    def get_repo(self):
        if self.url: # User is using the -fc (--from-clone) option
            if path.exists(self.rpath) and path.isdir(self.rpath): # Repo might already exist
                try:
                    r = Repo(self.rpath) # Attempt to access repo
                    if self.branch: # User is looking for specific branch
                        try:
                            b = r.active_branch
                        except TypeError: # Branch is detached
                            return logger.error(f"The repository you are cloning from already exists, but the branch you specified ({self.branch}) is detached. Exiting...")
                        if not str(b) == str(self.branch): # Branch of existing repo is not the branch the user wants
                            return logger.error(f"The repository you are cloning from already exists, but the active branch ({b}) does not match the branch you specified ({self.branch}). Exiting...")
                    logger.warn("The repository you are cloning from already exists. Cloning process terminated, accessing it normally instead.")
                    return r # Repo was accessed with no problems
                
                except GitCommandError: 
                    return logger.error("The repository you are cloning from already exists but is not a valid repository. Exiting...")
                
                except InvalidGitRepositoryError:
                    return logger.error("Invalid git repository. Exiting...")
                        
            try: # Try to clone
                r = Repo.clone_from(self.url, self.rpath, branch=self.branch, no_checkout=True)
            except GitCommandError:
                logger.error(f"The repository {self.url} does not exist or is invalid. Attempting to delete tree...")
                return "deltree"
            
        else: # Just access repo normally
            try:
                r = Repo(self.rpath)
                if self.branch:
                    try:
                        b = r.active_branch
                    except TypeError:
                        return logger.error(f"The repository you are accessing already exists, but the branch you specified ({self.branch}) is detached. Exiting...")
                    if not str(b) == str(self.branch): # Branch of repo is not the branch the user wants
                        return logger.error(f"The repository you are accessing already exists, but the active branch ({b}) does not match the branch you specified ({self.branch}). Exiting...")
                    
            except InvalidGitRepositoryError:
                return logger.error("Invalid git repository. Exiting...")
        
        return r

    def gather_commits(self):
        commits = list(
            self.r.iter_commits(
                since=self.start_date,
                until=self.end_date,
                rev=self.branch,
            )
        )
        logger.info(f"Gathered {len(commits)} commit(s) based on since, until and rev information.")
        
        return commits
    
    def instantiate_commits(self):
        commit_objects = []
        for commit in self.raw_commits:
            commit_objects.append(Commit(self.owner, self.rname, self.branch, commit))

        return commit_objects

    def filter_commits(self):
        filtered_commits = self.commit_objects
        
        if self.queries_any or self.queries_all:
            queries, query_func = (self.queries_any, any) if self.queries_any else (self.queries_all, all)
            filtered_commits = [commit for commit in self.commit_objects if query_func(q in commit["description"] or q in commit["title"] for q in queries)]        
            logger.info(f"Filtered {len(filtered_commits)} commit(s) from {len(self.commit_objects)} existing commits based on query")
            
        if self.authors:
            prior_len = len(filtered_commits)
            filtered_commits = [commit for commit in filtered_commits if commit["author_email"] in self.authors]
            logger.info(f"Filtered {len(filtered_commits)} commit(s) from {prior_len} commit(s) based on author name.")
            
        if self.newest_n_commits:
            if not self.newest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[:self.newest_n_commits]
                logger.info(f"Selecting n newest number of commits ({self.newest_n_commits}).")
            else:
                logger.warn(f"Newest n number of commits ({self.newest_n_commits}) could not be selected as it is greater than or equal to the current amount of commits")
        elif self.oldest_n_commits:
            if not self.oldest_n_commits >= len(filtered_commits):
                filtered_commits = filtered_commits[-self.oldest_n_commits:]
                logger.info(f"Selecting n oldest number of commits ({self.oldest_n_commits}).")
            else: 
                logger.warn(f"Oldest n number of commits ({self.oldest_n_commits}) could not be selected as it is greater than or equal to the current amount of commits")

        step = -1 if not self.reverse else 1
        filtered_commits = filtered_commits[::step] 
        
        return filtered_commits

class Commit(dict):
    def __init__(self, owner, rname, branch, commit: Repo.commit):
        self["rname"] = rname 
        self["branch"] = branch
        self["author_name"] = commit.author
        self["author_email"] = commit.author.email
        self["date"] = datetime.fromtimestamp(commit.committed_date)
        self["hexsha_short"] = commit.hexsha[:7]
        self["hexsha_long"] = commit.hexsha
        self["diff_url"] = f"https://github.com/{owner}/{rname}/commit/{commit.hexsha}"
        
        msg = commit.message.split("\n")
        self["title"] = msg[0]
        if len(msg) > 1:
            self["description"] = "\n".join(msg[1:])
        else:
            self["description"] = ""
    
    def __str__(self):
        return f"""
=============================
Repository: {self["rname"]}\n
Commit {self["hexsha_short"]}: Commited by {self["author_name"]} ({self["author_email"]}) to {self["branch"]} on {self["date"]}\n
{self["title"]}\n{self["description"]}\nView diff: {self["diff_url"]}
=============================
"""
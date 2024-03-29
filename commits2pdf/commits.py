from os import path
from datetime import datetime

from git import Repo

from .logger import logger

class Commits(object):
    def __init__(self, **kwargs):
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
        self.queries = kwargs["queries"]

        self.r = self.get_repo()  
        self.rname = path.basename(self.r.working_dir)     
        self.raw_commits: list[Repo.commit] = self.gather_commits()
        self.commit_objects: list[Commit] = self.instantiate_commits()
        self.filtered_commits: list[Commit] = self.filter_commits()

    def get_repo(self):
        if self.url:
            r = Repo.clone_from(self.url, self.rpath, branch=self.branch)
        else: 
            r = Repo(self.rpath)
        
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
        
        if self.queries:
            filtered_commits = [commit for commit in self.commit_objects for q in self.queries if q in commit["description"] or q in commit["title"]]
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
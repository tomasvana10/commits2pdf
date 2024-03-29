from os import path
from datetime import datetime

import git

class Commits(object):
    def __init__(self, **kwargs):
        self.rpath: str = kwargs["rpath"]
        self.owner: str = kwargs["owner"]
        self.url: str = kwargs["url"]
        self.branch: str = kwargs["branch"]
        self.authors: list[str] = kwargs["authors"]
        self.start_date = kwargs["start_date"]
        self.end_date = kwargs["end_date"]

        self.r = self.get_repo()  
        self.rname = path.basename(self.r.working_dir)     
        self.commits = self.gather_commits()
        self.formatted_commits: list[Commit] = self.format_commits()

    def get_repo(self):
        if self.url:
            r = git.Repo.clone_from(self.url, self.rpath, branch=self.branch)
        else: 
            r = git.Repo(self.rpath)
        
        return r

    def gather_commits(self):
        commits = list(
            self.r.iter_commits(
                since=self.start_date,
                until=self.end_date,
                rev=self.branch,
            )
        )[::-1]
        
        filtered_commits = commits
        if self.authors:
            filtered_commits = [commit for commit in commits if commit.author.email in self.authors]
        
        return filtered_commits
    
    def format_commits(self):
        commits = []
        for commit in self.commits:
            commits.append(Commit(self.owner, self.rname, self.branch, commit))
        
        return commits

class Commit(dict):
    def __init__(self, owner, rname, branch, commit: git.Repo.commit):
        self["rname"] = rname 
        self["branch"] = branch
        self["author_name"] = commit.author.name
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
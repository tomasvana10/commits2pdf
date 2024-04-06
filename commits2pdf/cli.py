from argparse import ArgumentParser
from datetime import datetime
from re import match
from os import path, startfile
from os import system as os_system
from platform import system

from .render2 import PDF
from .commits import Commits
from .constants import DATE, EMAILS, QUERY, LIGHT, DARK
from .logger import logger

USAGE_INFO = """Simply run ``c2p -O <owner_name>`` in the command-line to generate a PDF of your repo's commit history 
(assuming your current directory is a repository).
""" 
INVALID_ARG_MSG = """"Invalid {} format. Run commits2pdf-h for more information."""

def main():
    parser = ArgumentParser(description="Commits to PDF", prog="commits2pdf", epilog=USAGE_INFO)
    parser.add_argument("-O", "--owner", dest="owner", required=True, help="The owner of the git repository. Required.")
    parser.add_argument("-o", "--output", dest="output", default=".", help="Path to your PDF output. Set to \".\" by default.")
    parser.add_argument("-b", "--branch", dest="branch", default="main", type=str, help="The repository branch. Set to \"main\" by default.")
    parser.add_argument("-a", "--authors", dest="authors", help="Filter commits from a comma-separated list of authors. Format: <author@email.com> OR <author1@email.com,author2@email.com> etc. Set to all authors by default.")
    parser.add_argument("-s", "--start_date", dest="start_date", help="Filter from start date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05")
    parser.add_argument("-e", "--end_date", dest="end_date", help="Filter to end date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05")
    parser.add_argument("-r", "--reverse", dest="reverse", action="store_true", help="Output the commits from newest to oldest. Set to oldest to newest by default")
    parser.add_argument("-l", "--light", dest="light", action="store_true", help="Toggle light mode for the output PDF. Set to \"dark\" by default.") 
    parser.add_argument("-po", "--prevent-open", dest="prevent_open", action="store_true", help="Prevent the program from automatically opening the directory the PDF was created in.")
    
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument("-qa", "--query-any", dest="queries_any", help="Select the commits whose title OR description match ANY part of your query. Format: <query1> OR <query1,query2> etc")
    query_group.add_argument("-QA", "--query-all", dest="queries_all", help="Select the commits whose title OR description match ALL parts of your query. Format: <query1> OR <query1,query2> etc")
    
    repo_group = parser.add_mutually_exclusive_group()
    repo_group.add_argument("-rp", "--repo-path", dest="rpath", default=".", type=str, help="Path to your repository directory. Set to \".\" by default.")
    repo_group.add_argument("-fc", "--repo-from-clone", dest="rname", type=str, help="Clone a repo into the working directory and generate the commits PDF from it automatically. Format: <repo name>")
    
    n_commits_group = parser.add_mutually_exclusive_group()
    n_commits_group.add_argument("-nnc", "--newest-n-commits", dest="newest_n_commits", type=int, help="Select the newest n number amount of commits to include after filtering.")
    n_commits_group.add_argument("-onc", "--oldest-n-commits", dest="oldest_n_commits", type=int, help="Select the oldest n number amount of commits to include after filtering.")
    
    args = parser.parse_args()
    
    appearance, rpath, url, authors, start_date, end_date, queries_any, queries_all = handle_arguments(args)

    if args.rname:
        logger.warn("When using -fc or --repo-from-clone: Entering an invalid --owner arg will result in an error.")
    if args.rpath and not args.rname:
        logger.warn("When accessing a repo normally with -rp: Entering an invalid --owner arg will result in invalid diff links in the output PDF.")
        logger.warn("If the directory name of the repo you are accessing has been renamed, invalid diff links in the output PDF may be present.")
    
    commits = Commits(
        rpath=rpath,
        owner=args.owner,
        url=url,
        branch=args.branch,
        authors=args.authors,
        start_date=start_date,
        end_date=end_date,
        reverse=args.reverse,
        newest_n_commits=args.newest_n_commits,
        oldest_n_commits=args.oldest_n_commits,
        queries_any=queries_any,
        queries_all=queries_all
    )
    
    if commits.err_flag: return

    pdf = PDF(
        commits,
        args.output,
        f"{commits.rname}-commits_report.pdf",
        appearance
    )
    
    p = path.abspath(args.output)
    logger.info(f"{commits.rname}-commits_report.pdf successfully generated in {p}")
    
    if not args.prevent_open:
        plat = system()
        if plat == "Windows":
            startfile(p)
        elif plat == "Darwin":
            system("open %s" % p)
        elif plat == "Linux":
            os_system("xdg-open %s" % p)
        
def handle_arguments(args):
    url = authors = start_date = end_date = queries_any = queries_all = None
    appearance = DARK if not args.light else LIGHT
    
    if args.rname:
        rpath = args.rname # Set the repository path to the name of the repository that will be cloned
        url = f"https://github.com/{args.owner}/{args.rname}"
    else:
        rpath = args.rpath
    
    if args.authors:
        if not match(EMAILS, args.authors):
            raise Exception(INVALID_ARG_MSG.format("email"))
        authors = args.authors.split(",")

    if args.start_date:
        if not match(DATE, args.start_date):
            raise Exception(INVALID_ARG_MSG.format("date"))
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        if not match(DATE, args.end_date):
            raise Exception(INVALID_ARG_MSG.format("date"))
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    if args.queries_any:
        if not match(QUERY, args.queries_any):
            raise Exception(INVALID_ARG_MSG.format("query"))
        queries_any = args.queries_any.split(",")
    if args.queries_all:
        if not match(QUERY, args.queries_all):
            raise Exception(INVALID_ARG_MSG.format("query"))
        queries_all = args.queries_all.split(",")
    
    return appearance, rpath, url, authors, start_date, end_date, queries_any, queries_all
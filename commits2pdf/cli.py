import argparse
from datetime import datetime
from re import match

from .render import make_pdf
from .commits import Commits
from .constants import MATCH_DATE, EMAILS, LIGHT, DARK

USAGE_INFO = """Simply run ``commits2pdf -ow <owner_name>`` in the command-line to generate a PDF of your repo's commit history 
(assuming your current directory is a repository). The outupt is always in your current working directory.
""" 

def main():
    parser = argparse.ArgumentParser(description="Commits to PDF", prog="commits2pdf", epilog=USAGE_INFO)
    parser.add_argument("-ow", "--owner_name", dest="owner", required=True, help="The owner of the git repository. Required to view diffs in the PDF.")
    parser.add_argument("-rp", "--repo-path", dest="rpath", default=".", type=str, help="Path to your repository. Set to \".\" by default.")
    parser.add_argument("-fc", "--repo-from-clone", dest="rname", type=str, help="Clone a repo and generate the commits PDF from it automatically. Format: <repo name>")
    parser.add_argument("-b", "--branch", dest="branch", default="main", type=str, help="Specify your repository branch. Set to \"main\" by default.")
    parser.add_argument("-l", "--light", dest="light", action="store_true", help="Toggle light mode for the output PDF. Set to \"dark\" by default.")
    parser.add_argument("-a", "--authors", dest="authors", help="Specify commits from a selection of authors. Format: <author@email.com> OR <author1@email.com,author2@email.com> etc. Set to all authors by default.")
    parser.add_argument("-s", "--start_date", dest="start_date", help="Start date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05")
    parser.add_argument("-e", "--end_date", dest="end_date", help="End date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05")
    
    args = parser.parse_args()
    
    appearance, rpath, url, authors, start_date, end_date = handle_arguments(args)

    commits = Commits(
        rpath=rpath,
        owner=args.owner,
        url=url,
        branch=args.branch,
        authors=args.authors,
        start_date=start_date,
        end_date=end_date
    )
    
    make_pdf(commits, f"{commits.rname}-commits_report.pdf", appearance)
    print(f"PDF successfully generated!")

def handle_arguments(args):
    appearance = DARK if not args.light else LIGHT
    
    url = None
    if args.rname:
        rpath = args.rname # Set the repository path to the name of the repository that will be cloned
        url = f"https://github.com/{args.owner}/{args.rname}"
    else:
        rpath = args.rpath
    
    authors = None
    if args.authors:
        if not match(EMAILS, args.authors):
            raise Exception("Invalid email format. Run commits2pdf -h for more information.")
        authors = args.authors.split(",")
    
    start_date, end_date = None, None
    if args.start_date:
        if not match(MATCH_DATE, args.start_date):
            raise Exception("Invalid date format. Run commits2pdf -h for more information.")
        else:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        if not match(MATCH_DATE, args.end_date):
            raise Exception("Invalid date format. Run commits2pdf -h for more information.")
        else:
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    return appearance, rpath, url, authors, start_date, end_date
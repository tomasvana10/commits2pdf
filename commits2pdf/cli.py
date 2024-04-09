"""Console entry point for ``commits2pdf``. Uses the ``argparse`` module to 
handle arguments. Imports a PDF generation implementation from this package 
(either ``pycairo`` or ``fpdf``) based on the users input.
"""

from argparse import ArgumentParser, Namespace
from datetime import datetime
from re import match
from os import path
from typing import Tuple, List, Dict, Union

from .commits import Commits
from .constants import (
    DATE, EMAILS, QUERY, USAGE_INFO, INVALID_ARG_WARNING, CAIRO_LIGHT, CAIRO_DARK,
    FPDF_LIGHT, FPDF_DARK, CANNOT_USE_SCALE_WARNING
)
from .logger import logger


def main() -> None:
    """Parses arguments, provides warnings, and collects the commits based on
    the arguments using the ``Commits`` class.
    """
    # General arguments group
    parser = ArgumentParser(description="Commits to PDF", prog="commits2pdf", 
                            epilog=USAGE_INFO)
    parser.add_argument("-O", "--owner", dest="owner", required=True,
                        help="The owner of the git repository. Required.")
    parser.add_argument("-o", "--output", dest="output", default=".", 
                        help="Path to your PDF output. Set to \".\" by default.")
    parser.add_argument("-b", "--branch", dest="branch", default="main", type=str, 
                        help="The repository branch. Set to \"main\" by default.")
    parser.add_argument("-a", "--authors", dest="authors", 
        help="Filter commits from a comma-separated list of authors. Format: "
             "<author@email.com> OR <author1@email.com,author2@email.com> etc. "
             "Set to all authors by default.")
    parser.add_argument("-s", "--start_date", dest="start_date", 
        help="Filter from start date of commits. Format: YYYY-mm-dd or YYYY-m-d. "
             "Example: 2023-12-05")
    parser.add_argument("-e", "--end_date", dest="end_date", 
        help="Filter to end date of commits. Format: YYYY-mm-dd or YYYY-m-d.  "
             "Example: 2023-12-05")
    parser.add_argument("-r", "--reverse", dest="reverse", action="store_true", 
        help="Output the commits from newest to oldest. Set to oldest to newest "
             "by default")
    parser.add_argument("-d", "--dark", dest="dark", action="store_true", 
        help="Toggle dark mode for the output PDF. Set to \"light\" by default.") 
    parser.add_argument("-po", "--prevent-open", dest="prevent_open", 
        action="store_true", 
        help="Prevent the program from automatically opening the directory the "
             "PDF was created in.")
    parser.add_argument("-sc", "--scaling", dest="scaling", type=float, default=1.0,
        help="Set the scaling of the output PDF. Only available with gen2a and gen2b.")
    
    # Group for the selection of a PDF generation implementation
    gen_group = parser.add_mutually_exclusive_group()
    gen_group.add_argument("-gen1", "--pdf_gen_1", action="store_true", 
        dest="gen1",
        help="PDF rendering implementation with ``pycairo``.")
    gen_group.add_argument("-gen2a", "--pdf_gen_2a", action="store_true", 
        dest="gen2a",
        help="The first PDF rendering implementation with ``fpdf``.")
    gen_group.add_argument("-gen2b", "--pdf_gen_2b", action="store_true", 
        dest="gen2b",
        help="The second PDF rendering implementation with ``pycairo``. The "
             "default option.")
    
    # Group for either an AND or OR query
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument("-qa", "--query-any", dest="queries_any", 
        help="Select the commits whose title OR description match ANY part of "
             "your query. Format: \"<query1>\" OR \"<query1,query2>\" etc. Note: "
             "queries can have leading or trailing whitespace.")
    query_group.add_argument("-QA", "--query-all", dest="queries_all", 
        help="Select the commits whose title OR description match ALL parts of "
             "your query. Format: \"<query1>\" OR \"<query1,query2>\" etc. Note: "
             "queries can have leading or trailing whitespace.")
    
    # Group for specifying either a path to a git repo or the name of the repo
    # to clone from
    repo_group = parser.add_mutually_exclusive_group()
    repo_group.add_argument("-rp", "--repo-path", dest="rpath", default=".", 
        type=str, help="Path to your repository directory. Set to \".\" by default.")
    repo_group.add_argument("-fc", "--repo-from-clone", dest="rname", type=str, 
        help="Clone a repo into the working directory and generate the commits "
             "PDF from it automatically. Format: <repo name> (case insensitive).")
    
    # Group for selecting either the newest or oldest n number of commits
    n_commits_group = parser.add_mutually_exclusive_group()
    n_commits_group.add_argument("-nnc", "--newest-n-commits", 
        dest="newest_n_commits", type=int, 
        help="Select the newest n number amount of commits to include after "
             "filtering.")
    n_commits_group.add_argument("-onc", "--oldest-n-commits", 
        dest="oldest_n_commits", type=int, 
        help="Select the oldest n number amount of commits to include after "
             "filtering.")
    
    args: Namespace = parser.parse_args()
    appearance, rpath, url, authors, start_date, end_date, queries_any, \
        queries_all, gen, mode, scaling = _handle_arguments(args)
    
    # Log some warnings based on where the user is using the --repo-from-clone 
    # option just accessing a preexisting git repo
    if args.rname:
        logger.warn("When using -fc or --repo-from-clone: Entering an invalid "
                    "--owner arg will result in an error.")
    if args.rpath and not args.rname:
        logger.warn("When accessing a repo normally with -rp: Entering an "
                    "invalid --owner arg will result in invalid diff links in "
                    "the output PDF.")
        logger.warn("If the directory name of the repo you are accessing has "
                    "been renamed, invalid diff links in the output PDF may be "
                    "present.")

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
    
    if not commits.err_flag:
        _make_pdf(commits, appearance, args, gen, mode, scaling) 
    else: return # Any errors would have been logged by ``commits.py``, so exit

def _make_pdf(commits: Commits, 
              appearance: str, 
              args: Namespace,
              gen: str,
              mode: str,
              scaling: int
              ) -> None:
    """Generate the PDF based on the user's specified generation module."""
    gen_args = [commits, args.output, f"{commits.rname}-commits_report.pdf", 
                appearance]
    
    if gen == "gen1":
        from .render_cairo import Cairo_PDF
        cls = Cairo_PDF
    else:
        from .render_fpdf import FPDF_PDF
        cls = FPDF_PDF
        gen_args.append(mode)
        gen_args.append(scaling)
    
    pdf = cls(*gen_args)
    try:
        if pdf.recursion_err_flag: return
    except: ...
    p = path.abspath(args.output)
    logger.info(f"{commits.rname}-commits_report.pdf successfully generated in {p}")

    if not args.prevent_open: _open_pdf(args, p)
    
def _open_pdf(args, p) -> None:
    """Open the PDF in the user's file system, unless the user has prevent open 
    flag (``-po`` or ``--prevent-open``) enabled.
    """
    if not args.prevent_open:
        from platform import system
        plat: str = system()
        if plat == "Windows":
            from os import startfile
            startfile(p)
        else:
            from os import system as os_system
            if plat == "Darwin":
                os_system("open %s" % p)
            elif plat == "Linux":
                os_system("xdg-open %s" % p)
        
def _handle_arguments(args: Namespace) -> Tuple[Union[None, str, List[str]]]:
    """Process arguments through some conditions and regex matching to ensure
    they are valid. Raise errors if they are not valid.
    """
    url = authors = start_date = end_date = queries_any = queries_all = scaling = None
    
    if args.rname:
        rpath: str = args.rname # Set the repository path to the name of the 
                                # repository that will be cloned
        url: str = f"https://github.com/{args.owner}/{args.rname}"
    else:
        rpath: str = args.rpath
    
    if args.authors:
        if not match(EMAILS, args.authors):
            logger.error(INVALID_ARG_WARNING.format("email"))
            exit(1)
        authors: List[str] = args.authors.split(",")

    if args.start_date:
        if not match(DATE, args.start_date):
            logger.error(INVALID_ARG_WARNING.format("date"))
            exit(1)
        start_date: datetime = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        if not match(DATE, args.end_date):
            logger.error(INVALID_ARG_WARNING.format("date"))
            exit(1)
        end_date: datetime = datetime.strptime(args.end_date, "%Y-%m-%d")

    if args.queries_any:
        if not match(QUERY, args.queries_any):
            logger.error(INVALID_ARG_WARNING.format("query"))
            exit(1)
        queries_any: List[str] = args.queries_any.split(",")
    elif args.queries_all:
        if not match(QUERY, args.queries_all):
            logger.error(INVALID_ARG_WARNING.format("query"))
            exit(1)
        queries_all: List[str] = args.queries_all.split(",")
    
    if args.gen1:
        gen, mode = "gen1", None
        appearance: Dict[str, Tuple[int]] = CAIRO_LIGHT if not args.dark \
                                            else CAIRO_DARK
        if args.scaling:
            logger.warning(CANNOT_USE_SCALE_WARNING)
    else:
        gen, mode = ("gen2a", "stable") if args.gen2a else ("gen2b", "unstable")
        appearance: Dict[str, Tuple[int]] = FPDF_LIGHT if not args.dark \
                                            else FPDF_DARK
        scaling = args.scaling
        
    return appearance, rpath, url, authors, start_date, end_date, queries_any, \
           queries_all, gen, mode, scaling
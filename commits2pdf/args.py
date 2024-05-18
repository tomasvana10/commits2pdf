"""Adds all the arguments to an instance of ``ArgumentParser``."""

from argparse import ArgumentParser

from .constants import FILENAME, USAGE_INFO

# General arguments
parser = ArgumentParser(
    description="Commits to PDF", prog="commits2pdf", epilog=USAGE_INFO
)
parser.add_argument(
    "owner",
    help="The owner of the git repository. Required.",
)

parser.add_argument(
    "-o",
    "--output",
    dest="output",
    default=".",
    help=(
        'Directory path to your PDF output. Set to "." (your current'
        " directory) by default. Will be created if it does not exist."
        " Example: ./work/my_pdfs"
    ),
)
parser.add_argument(
    "-n",
    "--name",
    dest="name",
    default=FILENAME,
    help=(
        'The name of your outputted PDF file. Set to "<repo_name>-commit_report" '
        "by default."
    ),
)

parser.add_argument(
    "-b",
    "--branch",
    dest="branch",
    default="main",
    type=str,
    help='The repository branch. Set to "main" by default.',
)
parser.add_argument(
    "-a",
    "--authors",
    dest="authors",
    help=(
        "Filter commits from a comma-separated list of authors. Format: "
        "<author@email.com> OR <author1@email.com,author2@email.com> etc. "
        "Set to all authors by default."
    ),
)
parser.add_argument(
    "-s",
    "--start-date",
    dest="start_date",
    help="Filter from start date of commits. Format: d/m/YYYY. Example: 5/12/2023",
)
parser.add_argument(
    "-e",
    "--end-date",
    dest="end_date",
    help="Filter to end date of commits. Format: d/m/YYYY. Example: 5/12/2023",
)
parser.add_argument(
    "-r",
    "--reverse",
    dest="reverse",
    action="store_true",
    help=(
        "Output the commits from newest to oldest. Set to oldest to newest "
        "by default"
    ),
)
parser.add_argument(
    "-d",
    "--dark",
    dest="dark",
    action="store_true",
    help='Toggle dark mode for the output PDF. Set to "light" by default.',
)
parser.add_argument(
    "-po",
    "--prevent-open",
    dest="prevent_open",
    action="store_true",
    help=(
        "Prevent commits2pdf from automatically opening the directory the "
        "PDF was created in."
    ),
)
parser.add_argument(
    "-sc",
    "--scaling",
    dest="scaling",
    type=float,
    default=1.0,
    help=(
        "Set the scaling of the output PDF. Only available with gen2a and"
        " gen2b."
    ),
)
parser.add_argument(
    "-in",
    "--include",
    dest="include",
    help=(
        "Include commits with the given string sequences in their title or"
        ' description. Format: "<string1>" OR "<string1,string2>". Whitespace'
        " sensitive and case insensitive. NOTE: This query is performed"
        " BEFORE excluding commits."
    ),
)
parser.add_argument(
    "-ex",
    "--exclude",
    dest="exclude",
    help=(
        "Exclude commits with the given string sequences in their title or"
        ' description. Format: "<string1>" OR "<string1,string2>". Whitespace'
        " sensitive and case insensitive."
    ),
)
parser.add_argument(
    "-q",
    "--quiet",
    dest="quiet",
    action="store_true",
    help="Suppress all logger messages except for errors.",
)

# Group for the selection of a PDF generation implementation
gen_group = parser.add_mutually_exclusive_group()
gen_group.add_argument(
    "-gen1",
    "--pdf-gen-1",
    action="store_true",
    dest="gen1",
    help="PDF rendering implementation with ``pycairo``.",
)
gen_group.add_argument(
    "-gen2a",
    "--pdf-gen-2a",
    action="store_true",
    dest="gen2a",
    help="The first PDF rendering implementation with ``fpdf``.",
)
gen_group.add_argument(
    "-gen2b",
    "--pdf-gen-2b",
    action="store_true",
    dest="gen2b",
    help=(
        "The second PDF rendering implementation with ``fpdf``. The "
        "default option."
    ),
)

# Group for specifying either a path to a git repo or the name of the repo
# to clone from
repo_group = parser.add_mutually_exclusive_group()
repo_group.add_argument(
    "-rp",
    "--repo-path",
    dest="rpath",
    default=".",
    type=str,
    help=(
        'Path to your repository directory. Set to "." (your current'
        " directory) by default."
    ),
)
repo_group.add_argument(
    "-fc",
    "--repo-from-clone",
    dest="rname",
    type=str,
    help=(
        "Clone a repo into the working directory and generate the commits "
        "PDF from it automatically. Format: <repo name> (case insensitive)."
    ),
)

# Group for selecting either the newest or oldest n number of commits
n_commits_group = parser.add_mutually_exclusive_group()
n_commits_group.add_argument(
    "-nc",
    "--newest-n-commits",
    dest="newest_n_commits",
    type=int,
    help=(
        "Select the newest n number amount of commits to include after "
        "filtering."
    ),
)
n_commits_group.add_argument(
    "-oc",
    "--oldest-n-commits",
    dest="oldest_n_commits",
    type=int,
    help=(
        "Select the oldest n number amount of commits to include after "
        "filtering."
    ),
)

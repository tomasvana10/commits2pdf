"""Console entry point for ``commits2pdf``. Uses the ``argparse`` module to
handle arguments. Imports a PDF generation implementation from this package
(either ``pycairo`` or ``fpdf``) based on the users input.
"""

from argparse import Namespace
from datetime import datetime
from os import path
from re import match, search

from .args import parser
from .commits import Commits
from .constants import (
    CAIRO_DARK,
    CAIRO_LIGHT,
    CANNOT_USE_SCALE_WARNING,
    DATE,
    EMAILS,
    FPDF_DARK,
    FPDF_LIGHT,
    INVALID_ARG_WARNING,
    INVALID_BASENAME_WARNING,
    INVALID_QUERIES,
)
from .logger import logger


def main() -> None:
    """Parses arguments, provides warnings, and collects the commits based on
    the arguments using the ``Commits`` class.
    """
    args: Namespace = parser.parse_args()
    (
        appearance,
        rpath,
        url,
        authors,
        start_date,
        end_date,
        include,
        exclude,
        gen,
        mode,
        scaling,
    ) = _validate_args(args)

    if args.rpath and not args.rname:
        logger.warn(INVALID_BASENAME_WARNING)

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
        include=include,
        exclude=exclude,
    )

    if not commits.err_flag:
        _make_pdf(commits, appearance, args, gen, mode, scaling)
    else:
        return  # Any errors would have been logged by ``commits.py``, so exit


def _make_pdf(
    commits: Commits,
    appearance: str,
    args: Namespace,
    gen: str,
    mode: str,
    scaling: int,
) -> None:
    """Generate the PDF based on the user's specified generation module."""
    gen_args = [
        commits,
        args.output,
        f"{commits.rname}-commits_report.pdf",
        appearance,
    ]

    if gen == "gen1":
        from .render_cairo import Cairo_PDF

        cls = Cairo_PDF
    else:
        from .render_fpdf import FPDF_PDF

        cls = FPDF_PDF
        gen_args.append(mode)
        gen_args.append(scaling)

    pdf = cls(*gen_args)
    if pdf.err_flag:
        return

    p = path.abspath(args.output)
    logger.info(
        f"Wrote {path.join(p, commits.rname)}-commits_report.pdf successfully!"
    )

    if not args.prevent_open:
        _open_pdf(args, p)


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


def _validate_args(args: Namespace) -> tuple[None | str | list[str]]:
    """Process arguments through some conditions and regex matching to ensure
    they are valid. Raise errors if they are not valid.
    """
    url = authors = start_date = end_date = include = exclude = scaling = None

    if args.rname:
        rpath: str = args.rname  # Set the repo path to the name of the repo 
                                 # that will be cloned
        url: str = f"https://github.com/{args.owner}/{args.rname}"
    else:
        rpath: str = args.rpath

    if args.authors:
        if not match(EMAILS, args.authors):
            logger.error(INVALID_ARG_WARNING.format("email"))
            exit(1)
        authors: list[str] = args.authors.split(",")

    if args.start_date:
        if not match(DATE, args.start_date):
            logger.error(INVALID_ARG_WARNING.format("date"))
            exit(1)
        start_date: datetime = datetime.strptime(args.start_date, "%d/%m/%Y")
    if args.end_date:
        if not match(DATE, args.end_date):
            logger.error(INVALID_ARG_WARNING.format("date"))
            exit(1)
        end_date: datetime = datetime.strptime(args.end_date, "%d/%m/%Y")

    if args.include:
        if search(INVALID_QUERIES, args.include):
            logger.error(INVALID_ARG_WARNING.format("query"))
            exit(1)
        include: list[str] = args.include.split(",")
        
    if args.exclude:
        if search(INVALID_QUERIES, args.exclude):
            logger.error(INVALID_ARG_WARNING.format("query"))
            exit(1)
        exclude: list[str] = args.exclude.split(",")

    if args.gen1:
        gen, mode = "gen1", None
        appearance: dict[str, tuple[int]] = (
            CAIRO_LIGHT if not args.dark else CAIRO_DARK
        )
        if args.scaling != 1.0:
            logger.warning(CANNOT_USE_SCALE_WARNING)
    else:
        gen, mode = (
            ("gen2a", "stable") if args.gen2a else ("gen2b", "unstable")
        )
        appearance: dict[str, tuple[int]] = (
            FPDF_LIGHT if not args.dark else FPDF_DARK
        )
        scaling = args.scaling

    return (
        appearance,
        rpath,
        url,
        authors,
        start_date,
        end_date,
        include,
        exclude,
        gen,
        mode,
        scaling,
    )

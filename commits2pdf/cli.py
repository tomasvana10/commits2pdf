"""Console entry point for ``commits2pdf``. Uses the ``argparse`` module to
handle arguments. Imports a PDF generation implementation from this package
(either ``pycairo`` or ``fpdf``) based on the users input.
"""

from argparse import Namespace
from datetime import datetime
from logging import ERROR
from os import path
from re import match, search
from typing import Dict, List, Tuple, Union

from pathvalidate import ValidationError, validate_filename, validate_filepath

from .args import parser
from .commits import Commits
from .constants import (
    CAIRO_DARK,
    CAIRO_DEPRECATION_ERROR,
    CAIRO_LIGHT,
    CANNOT_USE_SCALE_WARNING,
    DATE,
    EMAILS,
    FILENAME,
    FPDF_DARK,
    FPDF_LIGHT,
    INVALID_ARG_WARNING,
    INVALID_BASENAME_WARNING,
    INVALID_FILENAME_ERROR,
    INVALID_OUTPUT_DIR_ERROR,
    INVALID_QUERIES,
)
from .logger import logger


def main() -> None:
    """Parses arguments, provides warnings, and collects the commits based on
    the arguments using the ``Commits`` class.
    """
    args: Namespace = parser.parse_args()
    if args.quiet:  # Suppress all logs except for errors
        logger.setLevel(ERROR)
    try:
        validate_filepath(args.output)
    except ValidationError:
        logger.error(INVALID_OUTPUT_DIR_ERROR)
        exit(1)
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
        name,
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
        _make_pdf(commits, appearance, args, gen, mode, scaling, name)
    else:
        return  # Any errors would have been logged by ``commits.py``, so exit


def _make_pdf(
    commits: Commits,
    appearance: str,
    args: Namespace,
    gen: str,
    mode: str,
    scaling: int,
    name: str,
) -> None:
    """Generate the PDF based on the user's specified generation module."""
    output_filename = (
        FILENAME.format(commits.rname) if name == FILENAME else name
    )
    output_dir = path.abspath(args.output)
    full_output_path = path.join(output_dir, output_filename)
    gen_args = [
        commits,
        args.output,
        output_filename,
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

    logger.info(f"Wrote {full_output_path} successfully!")

    if not args.prevent_open:
        _open_pdf(args, output_dir)


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


def _validate_args(args: Namespace) -> Tuple[Union[None, str, List[str]]]:
    """Process arguments through some conditions and regex matching to ensure
    they are valid. Raise errors if they are not valid.
    """
    url = authors = start_date = end_date = include = exclude = scaling = None
    name = args.name

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
        authors: List[str] = args.authors.split(",")

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
        include: List[str] = args.include.split(",")

    if args.exclude:
        if search(INVALID_QUERIES, args.exclude):
            logger.error(INVALID_ARG_WARNING.format("query"))
            exit(1)
        exclude: List[str] = args.exclude.split(",")

    if args.gen1:
        try:
            import cairo
        except ImportError:
            logger.error(CAIRO_DEPRECATION_ERROR)
            exit(1)
        gen, mode = "gen1", None
        appearance: Dict[str, Tuple[int]] = (
            CAIRO_LIGHT if not args.dark else CAIRO_DARK
        )
        if args.scaling != 1.0:
            logger.warning(CANNOT_USE_SCALE_WARNING)
    else:
        gen, mode = (
            ("gen2a", "stable") if args.gen2a else ("gen2b", "unstable")
        )
        appearance: Dict[str, Tuple[int]] = (
            FPDF_LIGHT if not args.dark else FPDF_DARK
        )
        scaling = args.scaling

    if name != FILENAME:
        if not name.endswith(".pdf"):
            name += ".pdf"
    try:
        validate_filename(name)
    except ValidationError:
        logger.error(INVALID_FILENAME_ERROR)
        exit(1)

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
        name,
    )

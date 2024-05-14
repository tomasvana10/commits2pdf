from datetime import datetime
from os import makedirs, path
from pickle import dumps, loads
from time import time

from fpdf import FPDF
from tqdm import tqdm

from .constants import (
    FPDF_DARK,
    INFO_TEXT_FONT,
    MARGIN_FONT,
    MARGIN_LR,
    MARGIN_TB,
    MEDIUM_TEXT_FONT,
    MEDIUM_TEXT_FONT_BOLD,
    RECURSION_ERROR,
    SMALL_TEXT_FONT,
    SUBTITLE_FONT,
    TITLE_FONT,
    TITLE_PAGE_INFO_FONT,
    WRITING_PDF_INFO,
)
from .logger import logger


def footer():
    pass


def _beginpage_addon(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.set_fill_color(*FPDF_DARK["background"])
        self.rect(h=self.h, w=self.w, x=0, y=0, style="DF")
        return result

    return wrapper


class FPDF_PDF:
    """PDF generation class implementing 2 methods of generation (``gen2a`` and
    ``gen2b``.
    """

    def __init__(
        self,
        commits: object,
        output: str,
        filename: str,
        appearance: dict,
        mode: str,
        scaling: str,
    ) -> None:
        super().__init__()  # portrait; millimetres; a4
        FPDF_PDF._set_scaling(scaling)

        self.err_flag: bool = False
        self.timestamp = datetime.fromtimestamp(int(time())).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        self._commits, self._output, self._filename, self._ap, self._mode = (
            commits,
            output,
            filename,
            appearance,
            mode,
        )
        self.commit_count = len(self._commits.filtered_commits)

        if self._ap["TYPE"] == "DARK":  # Inject decorators to detect new page
            FPDF._beginpage = _beginpage_addon(FPDF._beginpage)
        self._p = FPDF()

        self._configure_fpdf()
        self._prepare_and_draw()
        logger.info(
            WRITING_PDF_INFO.format(
                path.normpath(self._output) + " ..."
                if self._output != "."
                else "your current directory..."
            )
        )
        self._write()

    @staticmethod
    def _set_scaling(scaling: float) -> None:
        """Scale the fonts based on the user-selected scaling. Set to 1.0 by
        default.
        """
        TITLE_FONT[2] *= scaling
        TITLE_PAGE_INFO_FONT[2] *= scaling
        SUBTITLE_FONT[2] *= scaling
        SMALL_TEXT_FONT[2] *= scaling
        MEDIUM_TEXT_FONT[2] *= scaling
        MEDIUM_TEXT_FONT_BOLD[2] *= scaling
        INFO_TEXT_FONT[2] *= scaling

    def _configure_fpdf(self):
        self._p.set_fill_color(*self._ap["background"])
        self._p.set_creator("commits2pdf")
        self._p.set_title(f"Commit Report - {self._commits.rname}")
        self._p.set_author(f"{self._commits.owner}")
        self._p.set_subject("Git Commit Report")
        self._p.set_keywords(
            "git;repo;repository;report;documentation;cli;python;git-commit"
        )
        self._p.set_margins(MARGIN_LR, MARGIN_TB)

    def _prepare_and_draw(self):
        self._p.add_page()
        self._draw_page_bg()
        self._draw_title_page()
        if self._mode == "unstable":
            self.do_pre_vis: bool = True
            self._p.set_auto_page_break(auto=False)
        else:
            self.do_pre_vis: bool = False
            self._p.set_auto_page_break(auto=True)

        if self.commit_count > 0:
            self._draw_commits()

    def footer(self) -> None:
        self._p.set_y(-1 * (MARGIN_TB / 2))
        self._set_font(*MARGIN_FONT)
        self._p.set_text_color(*self._ap["text"])
        self._p.cell(1, 0, f"Page {self._p.page_no()}", 0, 0, "L")
        self._p.cell(
            0, 0, f"Generated by commits2pdf at {self.timestamp}", 0, 0, "C"
        )

    def _draw_page_bg(self) -> None:
        """Draw the page background as a rectangle."""
        self._p.rect(h=self._p.h, w=self._p.w, x=0, y=0, style="DF")

    def _write(self) -> None:
        """Save the file where the user has specified."""
        if not path.exists(self._output):
            makedirs(self._output)
        self._p.output(path.join(self._output, self._filename), "F")

    def _set_font(
        self, *args: list[float], obj: str | object = "main"
    ) -> None:
        """Set the current font to a RGB value."""
        p = self._p if obj == "main" else obj
        p.set_font(args[0], args[1], args[2])

    def _draw_newpage_commit(self, commit, no_divider=False):
        """Draw a commit that cannot fit on the existing page."""
        self.footer()
        # Ensure that a new page is not added when drawing the commit (that is
        # a multipage commit) to prevent page 2 being empty.
        if self._p.page_no() == 2 and self.commit_counter == 0:
            self._p.set_y(MARGIN_TB)
        else:
            self._p.add_page()
        self._draw_page_bg()
        self._p.set_auto_page_break(auto=True, margin=MARGIN_TB)
        self._p.footer = (
            self.footer
        )  # Temporarily override the empty ``footer``
           # method inherited from ``FPDF`` to
           # automatically generate a footer if this
           # new commit spans more than a single page.
        page_no_before_draw = self._p.page
        self._draw_commit(commit, no_divider=no_divider)
        self._p.set_auto_page_break(auto=False)
        self._p.footer = footer  # Set the footer method of ``self._p`` back to
                                 # an empty method to prevent a recursion error
                                 # when cloning an instance of ``FPDF``.
        if self._p.page > page_no_before_draw:
            self.footer()
        self.commit_counter += 1

    def _draw_commits(self) -> None:
        """Driver function to draw all the commits using either the
        pre-visualisation method or the commit height estimation method.
        """
        self._p.add_page()  # Draw separate to the title page
        self._draw_page_bg()
        self.commit_counter: int = 0
        # gen2b
        if self._mode == "unstable":
            for commit in tqdm(
                self._commits.filtered_commits,
                ncols=85,
                desc="GENERATING",
            ):
                result = self._draw_commit(commit, pre_vis=True)
                if result == "NEW_PAGE_OK":  # Break page
                    self._draw_newpage_commit(commit)
                elif (
                    result == "NEW_PAGE_OK_BUT_NO_DIVIDER"
                ):  # The divider just barely doesn't fit
                    self._draw_newpage_commit(commit, no_divider=True)
                else:  # No need to break the page
                    self._draw_commit(commit)
                    self.commit_counter += 1
                    if self.commit_counter == self.commit_count:
                        self.footer()

        # gen2a
        elif self._mode == "stable":
            for commit in tqdm(
                self._commits.filtered_commits,
                ncols=85,
                desc="GENERATING",
            ):
                if self._commit_exceeds_size(commit):  # Break page
                    self._draw_newpage_commit(commit)
                else:
                    self._draw_commit(commit)
                    self.commit_counter += 1
                    if self.commit_counter == self.commit_count:
                        self.footer()

    def _get_pdf_object(self, pre_vis):
        if not pre_vis or not self.do_pre_vis:
            return self._p
        else:
            try:
                return loads(dumps(self._p))
            except RecursionError:
                logger.error(RECURSION_ERROR)
                self.err_flag = True
                exit(1)
            except Exception as ex:
                logger.error(
                    f"An unrecognised error occured: {type(ex).__name__}: {ex}"
                )
                self.err_flag = True
                exit(1)

    def _draw_commit(
        self,
        commit: dict[str, str],
        pre_vis: bool = False,
        no_divider: bool = False,
    ) -> str | None:
        """Draw all the parts of a commit to the current ``FPDF`` instance
        or a copy of it as part of the ``gen2b`` generation implementation.
        """
        p = self._get_pdf_object(pre_vis)

        p.set_text_color(*self._ap["text"])
        self._set_font(*INFO_TEXT_FONT, obj=p)
        p.multi_cell(w=0, h=p.font_size * 1.25, align="C", txt=commit["info"])
        p.ln(p.font_size * 0.75)
        # Tells the driver code that it must add a page
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95:
            return "NEW_PAGE_OK"

        self._set_font(*MEDIUM_TEXT_FONT_BOLD, obj=p)
        p.multi_cell(w=0, h=p.font_size * 1.25, align="L", txt=commit["title"])
        p.ln(-1 * p.font_size * 0.5)
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95:
            return "NEW_PAGE_OK"

        self._set_font(*SMALL_TEXT_FONT, obj=p)
        p.multi_cell(
            w=0, h=p.font_size * 1.5, align="L", txt=commit["description"]
        )
        p.ln()
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95:
            return "NEW_PAGE_OK"

        p.set_text_color(*self._ap["diff_url"])
        self._set_font(*SMALL_TEXT_FONT, obj=p)
        p.write(p.font_size * 1.5, "View diff on GitHub", commit["diff_url"])
        p.ln(p.font_size * 4.75)
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95:
            return "NEW_PAGE_OK"

        if pre_vis or not no_divider or not self.do_pre_vis:
            div_y = p.get_y() - p.font_size * 3.25 / 2
            self._p.set_draw_color(*self._ap["text"])
            p.line(p.l_margin, div_y, p.w - p.r_margin, div_y)
            self._p.set_draw_color(*self._ap["background"])
            if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.97:
                return "NEW_PAGE_OK_BUT_NO_DIVIDER"

    def _commit_exceeds_size(self, commit: dict[str, str]) -> bool:
        """Estimate the height of the upcoming commit to see if a new page must
        be added. It has a poor consistency that worsens with the increase/
        decrease of scaling. It is used as part of the gen2a generation
        implementation.
        """
        info_lines = (
            len(commit["info"]) * (INFO_TEXT_FONT[2] // 2)
        ) // self._p.w
        title_lines = (
            len(commit["title"]) * (MEDIUM_TEXT_FONT_BOLD[2] // 2)
        ) // self._p.w
        desc_lines = (
            len(commit["description"]) * (SMALL_TEXT_FONT[2] // 2)
        ) // self._p.w
        diff_lines = (
            len(commit["diff_url"]) * (SMALL_TEXT_FONT[2] // 2)
        ) // self._p.w

        height = (
            (info_lines * INFO_TEXT_FONT[2])
            + (title_lines * MEDIUM_TEXT_FONT_BOLD[2])
            + (desc_lines * SMALL_TEXT_FONT[2])
            + (diff_lines * SMALL_TEXT_FONT[2])
        )

        return height * 1.2 > self._p.h - self._p.get_y()

    def _draw_title_page(self) -> None:
        """Draw the title, repository name, and filtering information on the
        first page of the PDF.
        """
        # Title text ("Commit Report")
        self._set_font(*TITLE_FONT)
        self._p.set_text_color(*self._ap["text"])
        self._p.cell(
            w=0, h=self._p.font_size * 1.5, txt="Commit Report", align="C"
        )
        self._p.ln()

        # Subtitle for "Repository"
        self._set_font(*SUBTITLE_FONT)
        self._p.multi_cell(
            w=0,
            h=self._p.font_size * 1.25,
            txt=f"Repository: {self._commits.rname}",
            align="C",
        )
        self._p.ln(self._p.font_size)

        # Owner
        self._set_font(*TITLE_PAGE_INFO_FONT)
        self._p.multi_cell(
            0,
            self._p.font_size * 1.5,
            txt=f"Owner: {self._commits.owner}",
            align="C",
        )
        self._p.ln()

        # Author(s)
        if self._commits.authors:
            authors = self._commits.authors.split(",")
            txt = f"Authors: {', '.join(authors)}"
            if len(authors) == 1:
                txt = txt.replace("Authors: ", "Author: ")
        else:
            txt = "Authors: All"
        self._p.multi_cell(0, self._p.font_size * 1.5, align="C", txt=txt)
        self._p.ln()

        # Start and end date, omit if no data
        if self._commits.start_date or self._commits.end_date:
            self._p.multi_cell(
                0,
                self._p.font_size * 1.5,
                align="C",
                txt=f"Start date: "
                f"{self._commits.start_date.strftime('%d/%m/%Y') if self._commits.start_date else 'N/A'} "
                f"| End date: {self._commits.end_date.strftime('%d/%m/%Y') if self._commits.end_date else 'N/A'}",
            )
            self._p.ln()

        # Branch
        self._p.multi_cell(
            0,
            self._p.font_size * 1.5,
            align="C",
            txt=f"Branch: {self._commits.branch}",
        )
        self._p.ln()

        # Newest and oldest n commits, omit if no data
        if self._commits.newest_n_commits or self._commits.oldest_n_commits:
            self._p.multi_cell(
                0,
                self._p.font_size * 1.5,
                txt=f"Newest n commits: "
                f"{self._commits.newest_n_commits} | Oldest n commits: "
                f"{self._commits.oldest_n_commits}",
                align="C",
            )
            self._p.ln()

        # Include/exclude filters, omit if no data
        if self._commits.include:
            self._p.multi_cell(
                0,
                self._p.font_size * 1.5,
                align="C",
                txt=f"Including: "
                f"{', '.join(self._commits.include) if self._commits.include else 'No specification'}",
            )
            self._p.ln()
        if self._commits.exclude:
            self._p.multi_cell(
                0,
                self._p.font_size * 1.5,
                align="C",
                txt=f"Excluding: "
                f"{', '.join(self._commits.exclude) if self._commits.exclude else 'No specification'}",
            )
            self._p.ln()

        # Sorting
        self._p.multi_cell(
            0,
            self._p.font_size * 1.5,
            align="C",
            txt=f"Sorting: "
            f"{'Oldest to newest' if not self._commits.reverse else 'Newest to oldest'}",
        )
        self._p.ln()

        # Commit count
        self._p.multi_cell(
            0,
            self._p.font_size * 1.5,
            align="C",
            txt=f"Commit count: {len(self._commits.filtered_commits)}",
        )
        self._p.ln()

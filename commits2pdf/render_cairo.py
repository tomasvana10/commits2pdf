from datetime import datetime
from os import path
from textwrap import wrap
from time import time

from cairo import (
    FONT_SLANT_ITALIC,
    FONT_SLANT_NORMAL,
    FONT_WEIGHT_BOLD,
    FONT_WEIGHT_NORMAL,
    Context,
    PDFSurface,
)
from tqdm import tqdm

from .constants import (
    HEIGHT,
    MARGIN,
    WIDTH,
    WRITING_PDF_INFO,
)
from .logger import logger


class Cairo_PDF:
    def __init__(
        self,
        commits: object,
        output: str,
        filename: str,
        appearance: dict[str, tuple[int]],
    ) -> None:
        """Assign attributes for use across the instance and instantiate the
        core parts of a pycairo PDF.
        """
        self._commits, self._output, self._filename, self._ap = (
            commits,
            output,
            filename,
            appearance,
        )
        self.timestamp = datetime.fromtimestamp(int(time())).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        self.err_flag: bool = False

        self._s = PDFSurface(path.join(output, filename), WIDTH, HEIGHT)
        self._c = Context(self._s)
        self.page: int = 1
        self.y: int = MARGIN

        self._draw_bg()
        self._draw_footer()
        self._draw_title("Commit Report", self.y)
        self.y += 30
        self._draw_rname(commits.rname, self.y)
        self.y += 40

        if len(self._commits.filtered_commits) > 0:
            self._draw_commits()
            logger.info(
                WRITING_PDF_INFO.format(
                    path.normpath(self._output) + " ..."
                    if self._output != "."
                    else "your current directory..."
                )
            )
            self._s.finish()

    def _draw_commits(self) -> None:
        """Driver function to draw all the commits."""
        for commit in tqdm(
            self._commits.filtered_commits,
            ncols=85,
            desc="GENERATING",
        ):
            text = self._get_commit_text(commit)
            height = sum(len(t) for t in text) * 14 + 50
            if self.y + height + 25 > HEIGHT - MARGIN:
                self._s.show_page()
                self.page += 1
                self.y = MARGIN

                self._draw_bg()
                self._draw_footer()

            self.draw_commit(commit, self.y, *text)
            self.y += height + 50

    def _set_font(self, t: str, font: str = "Arial") -> None:
        """Set the font face, consisting of the family, slant and weight."""
        if t == "n":
            self._c.select_font_face(
                font, FONT_SLANT_NORMAL, FONT_WEIGHT_NORMAL
            )
        elif t == "b":
            self._c.select_font_face(font, FONT_SLANT_NORMAL, FONT_WEIGHT_BOLD)
        elif t == "i":
            self._c.select_font_face(
                font, FONT_SLANT_ITALIC, FONT_WEIGHT_NORMAL
            )

    def _draw_bg(self) -> None:
        """Draw the page background."""
        self._c.set_source_rgb(*self._ap["background"])
        self._c.rectangle(0, 0, WIDTH, HEIGHT)
        self._c.fill()

    def _draw_title(self, text: str, y: int) -> None:
        """Draw the "Commits Report" title for the first page."""
        self._c.set_source_rgb(*self._ap["text"])
        self._set_font("b")
        self._c.set_font_size(24)
        self._c.move_to(MARGIN, y)
        self._c.show_text(text)

    def _draw_footer(self) -> None:
        """Draw the footer for the current page."""
        self._c.set_source_rgb(*self._ap["text"])
        self._set_font("n")
        self._c.set_font_size(10)
        self._c.move_to(MARGIN, HEIGHT - MARGIN)
        self._c.show_text(f"Page {self.page}")
        self._set_font("i")
        self._c.move_to(MARGIN, HEIGHT - MARGIN + 20)
        self._c.show_text(f"Generated by commits2pdf on {self.timestamp}")

    def _draw_rname(self, rname: str, y: int) -> None:
        """Draw the repository name."""
        w_rname: list[str] = wrap(
            f"Repository: {rname}", width=(WIDTH - MARGIN * 2) // 8
        )
        self._draw_wrapped_text(w_rname, y, 18, "b")

    def _get_commit_text(self, commit: object) -> tuple[list[str]]:
        """Get the commit text for a commit and wrap it with a bunch of magic
        numbers.
        """
        info: list[str] = wrap(
            commit["info"], width=(WIDTH - MARGIN * 2) // 6.5
        )
        title: list[str] = wrap(
            commit["title"], width=(WIDTH - MARGIN * 2) // 8
        )
        diff_url: list[str] = wrap(
            commit["diff_url"], width=(WIDTH - MARGIN * 2) // 5
        )

        desc_lines: list[str] = commit["description"].split("\n")
        desc = []
        for line in desc_lines:
            lines = wrap(line, width=(WIDTH - MARGIN * 2) // 5)
            desc.extend(lines)
            if len(lines) > 1:
                desc.append("")

        return info, title, desc, diff_url

    def _draw_wrapped_text(
        self,
        lines: list[str],
        y: int,
        font_size: int,
        font_type: str,
        font_family: str = "Arial",
        rgb: str = "text",
    ) -> int:
        """Draw the wrapped text for a commit component line by line."""
        self._c.set_source_rgb(*self._ap[rgb])
        self._c.set_font_size(font_size)
        self._set_font(font_type, font=font_family)
        this_y: int = y
        for line in lines:
            self._c.move_to(MARGIN, this_y)
            self._c.show_text(line)
            this_y += 15

        return this_y + 15

    def draw_commit(
        self, commit: object, y: int, *args: tuple[list[str]]
    ) -> None:
        """Driver function for its own driver function idk."""
        new_y = self._draw_wrapped_text(
            args[0], y, 11, "n", font_family="Courier New"
        )  # Info
        new_y = self._draw_wrapped_text(
            args[1], new_y, 16, "b"
        )  # Commit Title
        new_y = self._draw_wrapped_text(args[2], new_y, 11, "n")  # Description
        new_y = self._draw_wrapped_text(
            args[3], new_y, 11, "n", rgb="diff_url"
        )  # Diff Url
        self._draw_divider(new_y)  # Horizontal Divider

    def _draw_divider(self, y: int) -> None:
        """Draw the horizontal divider between commits which is only centered
        around half the time for some reason.
        """
        self._c.set_source_rgb(*self._ap["text"])
        self._c.set_line_width(1)
        self._c.move_to(MARGIN, y)
        self._c.line_to(WIDTH - MARGIN, y)
        self._c.stroke()

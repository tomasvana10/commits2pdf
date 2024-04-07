from time import time
from datetime import datetime
from os import path
from pickle import loads, dumps
from typing import List, Dict, Union

from fpdf import FPDF

from .constants import (
    TITLE_FONT, SUBTITLE_FONT, MARGIN_FONT, SMALL_TEXT_FONT, MEDIUM_TEXT_FONT,
    MEDIUM_TEXT_FONT_BOLD, INFO_TEXT_FONT, MARGIN_LR, MARGIN_TB
)


class FPDF_PDF(FPDF):
    def __init__(self, 
                 commits: object, 
                 output: str, 
                 filename: str, 
                 appearance: dict, 
                 mode: str, 
                 scaling: str
                 ) -> None:
        """Assign attributes for use across the instance and configure the 
        settings of the ``FPDF`` class.
        """
        super().__init__() # portrait; millimetres; a4
        FPDF_PDF._set_scaling(scaling)
        self.timestamp = datetime.fromtimestamp(
            int(time())).strftime('%Y-%m-%d %H:%M:%S')
        self._commits, self._output, self._filename, self._ap, self._mode = \
            commits, output, filename, appearance, mode
        if self._mode == "unstable":
            self.do_pre_vis = True 
            self.set_auto_page_break(auto=False)
        else:
            self.do_pre_vis = False
            self.set_auto_page_break(auto=True)

        self.set_fill_color(*self._ap["background"])
        self.set_creator("commits2pdf")
        self.set_title(f"Commits Report - {self._commits.rname}")
        self.set_author(f"{self._commits.owner}")
        self.set_subject("Git Commit Report")
        self.set_keywords("git;repo;repository;report;documentation;cli;python")
        self.set_margins(MARGIN_LR, MARGIN_TB)
        self.add_page()
        self._draw_page_bg()
        self._draw_title_page()
        
        if len(self._commits.filtered_commits) > 0: self._draw_commits()
        self._write()
    
    @staticmethod
    def _set_scaling(scaling: float) -> None:
        """Scale the fonts based on the user-selected scaling. Set to 1.0 by
        default.
        """
        TITLE_FONT[2] *= scaling
        SUBTITLE_FONT[2] *= scaling
        SMALL_TEXT_FONT[2] *= scaling
        MEDIUM_TEXT_FONT[2] *= scaling
        MEDIUM_TEXT_FONT_BOLD[2] *= scaling
        INFO_TEXT_FONT[2] *= scaling
    
    def footer(self) -> None:
        """An override the footer function of the ``FPDF`` class, which is 
        empty.
        """
        self.set_y(-1 * (MARGIN_TB / 2))
        self._set_font(*MARGIN_FONT)
        self.set_text_color(*self._ap["text"])
        self.cell(1, 0, f"Page {self.page_no()}", 0, 0, "L")
        self.cell(0, 0, f"Generated by commits2pdf at {self.timestamp}", 0, 0, 
                  "C")
    
    def _draw_page_bg(self) -> None:
        """Draw the page background as a rectangle."""
        self.rect(h=self.h, w=self.w, x=0, y=0, style="DF")
    
    def _write(self) -> None:
        """Save the file where the user has specified."""
        self.output(path.join(self._output, self._filename), "F")
    
    def _set_font(self, 
                  *args: List[float]
                  ) -> None:
        """Set the current font to a red, green and blue value."""
        self.set_font(args[0], args[1], args[2])
    
    def _draw_commits(self) -> None:
        """Driver function to draw all the commits using either the 
        pre-visualisation method or with the commit height estimation method.
        """
        self.add_page()
        self._draw_page_bg()
        if self._mode == "unstable":
            for commit in self._commits.filtered_commits:
                if (result := self._draw_commit(commit, pre_vis=True)) == "new":
                    self.add_page()
                    self._draw_page_bg()
                    self._draw_commit(commit)
                elif result == "no_divider":
                    self._draw_commit(commit, no_divider=True)
                else:
                    self._draw_commit(commit)
        elif self._mode == "stable":
            for commit in self._commits.filtered_commits:
                if self._commit_exceeds_size(commit):
                    self.add_page()
                    self._draw_page_bg()
                self._draw_commit(commit)        
            
    def _draw_commit(self, 
                     commit: Dict[str, str], 
                     pre_vis: bool = False, 
                     no_divider: bool = False
                     ) -> Union[str, None]:
        """Draw all the parts of a commit to the current ``FPDF`` instance
        or a copy of it as part of the ``gen2b`` generation implementation.
        """
        p = self if not pre_vis or not self.do_pre_vis else loads(dumps(self))
        
        y: int = p.get_y()
        p.set_text_color(*self._ap["text"])
        p._set_font(*INFO_TEXT_FONT)
        p.multi_cell(w=0, h=p.font_size * 1.25, align="C", txt=commit["info"])
        p.ln(p.font_size * 0.75)
        # Tells the driver code that it must add a page
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95: return "new"
        
        p._set_font(*MEDIUM_TEXT_FONT_BOLD)
        p.multi_cell(w=0, h=p.font_size * 1.25, align="L", txt=commit["title"])
        p.ln(-1 * p.font_size * 0.5)
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95: return "new"

        p._set_font(*SMALL_TEXT_FONT)
        p.multi_cell(w=0, h=p.font_size * 1.5, align="L", 
                     txt=commit["description"])
        p.ln()
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95: return "new" 

        p.set_text_color(*self._ap["diff_url"])
        p._set_font(*SMALL_TEXT_FONT)
        p.write(p.font_size * 1.5, "View diff on GitHub", commit["diff_url"])
        p.ln(p.font_size * 4.75) 
        if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.95: return "new" 

        if pre_vis or not no_divider or not self.do_pre_vis:
            div_y = p.get_y() - p.font_size * 3.25 / 2
            self.set_draw_color(*self._ap["text"])
            p.line(p.l_margin, div_y, p.w - p.r_margin, div_y)
            self.set_draw_color(*self._ap["background"])
            if self.do_pre_vis and pre_vis and p.get_y() > p.h * 0.97: \
                return "no_divider" 

    def _commit_exceeds_size(self, 
                             commit: Dict[str, str]
                             ) -> bool:
        """Estimate the height of the upcoming commit to see if a new page must
        be added. It has a poor consistency that worsens with the increase/
        decrease of scaling. It is used as part of the gen2a generation
        implementation.
        """
        info_lines = (len(commit["info"]) * (INFO_TEXT_FONT[2] // 2)) // self.w
        title_lines = (len(commit["title"]) * (MEDIUM_TEXT_FONT_BOLD[2] // 2)) \
                       // self.w
        desc_lines = (len(commit["description"]) * (SMALL_TEXT_FONT[2] // 2)) \
                      // self.w
        diff_lines = (len(commit["diff_url"]) * (SMALL_TEXT_FONT[2] // 2)) \
                      // self.w

        height = (info_lines * INFO_TEXT_FONT[2]) \
                         + (title_lines * MEDIUM_TEXT_FONT_BOLD[2]) \
                         + (desc_lines * SMALL_TEXT_FONT[2]) \
                         + (diff_lines * SMALL_TEXT_FONT[2])

        return height > self.h - self.get_y()

    def _draw_title_page(self) -> None:
        """Draw the title, repository name, and filtering information on the
        first page of the PDF.
        """
        self._set_font(*TITLE_FONT)
        self.set_text_color(*self._ap["text"])
        self.cell(w=0, h=self.font_size * 1.5, txt="Commits Report", align="C")
        self.ln()
        
        self._set_font(*SUBTITLE_FONT)
        self.cell(w=0, h=self.font_size * 3, 
                  txt=f"Repository: {self._commits.rname}", align="C")
        self.ln()

        self._set_font(*MEDIUM_TEXT_FONT)
        self.multi_cell(0, self.font_size * 1.5, 
            txt=f"Owner: {self._commits.owner}", align="C")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, align="C",
            txt=f"Authors: "
                f"{', '.join(self._commits.authors.split(',')) if self._commits.authors else 'All'}")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, align="C",
            txt=f"Start date: "
                f"{self._commits.start_date.strftime('%Y-%m-%d') if self._commits.start_date else 'N/A'} "
                f"| End date: {self._commits.end_date.strftime('%Y-%m-%d') if self._commits.end_date else 'N/A'}")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, 
            txt=f"Newest n commits: "
                f"{self._commits.newest_n_commits} | Oldest n commits: "
                f"{self._commits.oldest_n_commits}",  align="C")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, align="C",
            txt=f"AND queries: "
                f"{', '.join(self._commits.queries_all) if self._commits.queries_all else 'None'}")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, align="C", 
            txt=f"OR queries: "
                f"{', '.join(self._commits.queries_any) if self._commits.queries_any else 'None'}")
        self.ln()
        self.multi_cell(0, self.font_size * 1.5, align="C",
            txt=f"Sorting: "
                f"{'Oldest to newest' if not self._commits.reverse else 'Newest to oldest'}")
        self.ln()
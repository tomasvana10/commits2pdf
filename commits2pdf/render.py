import textwrap
import os

import cairo

from .constants import WIDTH, HEIGHT, MARGIN


def make_pdf(commits, filename, appearance):
    global ap
    ap = appearance
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    c = cairo.Context(surface)

    c.set_source_rgb(*ap["background"])
    c.rectangle(0, 0, WIDTH, HEIGHT)
    c.fill()

    y = MARGIN  
    page = 1

    # Title
    draw_title(c, "Commit Report", y)
    y += 30
    draw_rname(c, commits.rname, y)
    y += 40

    for commit in commits.formatted_commits:
        if y + get_commit_height(commit) > HEIGHT - MARGIN:
            surface.show_page()
            page += 1
            y = MARGIN
            draw_page_number(c, page)  
            
            # Set background color for new page
            c.set_source_rgb(*ap["background"])
            c.rectangle(0, 0, WIDTH, HEIGHT)
            c.fill()

        draw_commit(c, commit, y)
        y += get_commit_height(commit) + 25

    surface.finish()

def draw_title(c, text, y):
    c.set_source_rgb(*ap["text"]) 
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(24)
    c.move_to(MARGIN, y)
    c.show_text(text)

def draw_rname(c, rname, y):
    c.set_source_rgb(*ap["text"]) 
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(18)
    c.move_to(MARGIN, y)
    c.show_text(f"Repository: {rname}")

def draw_commit(c, commit, y):
    c.set_source_rgb(*ap["text"]) 
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL) 

    # Misc info
    c.set_font_size(12)
    info_text = f"{commit['hexsha_short']} | Branch: {commit['branch']} | By {commit['author_name']} ({commit['author_email']}) | At {commit['date'].strftime('%Y-%m-%d')}"
    wrapped_info = textwrap.wrap(info_text , width=(WIDTH - MARGIN * 2) // 6)  
    info_y_pos = y
    for line in wrapped_info:
        c.move_to(MARGIN, info_y_pos)
        c.show_text(line)
        info_y_pos += 15 

    # Title
    c.set_font_size(16)
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    wrapped_title = textwrap.wrap(commit["title"], width=(WIDTH - MARGIN * 2) // 6)
    title_y_pos = info_y_pos + 15
    for line in wrapped_title:
        c.move_to(MARGIN, title_y_pos)
        c.show_text(line)
        title_y_pos += 15

    # Description 
    c.set_font_size(11)
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    wrapped_desc = textwrap.wrap(commit["description"], width=(WIDTH - MARGIN * 2) // 4.85)  
    desc_y_pos = info_y_pos + 35 
    for line in wrapped_desc:
        c.move_to(MARGIN, desc_y_pos)
        c.show_text(line)
        desc_y_pos += 15
    
    # Diff 
    c.set_source_rgb(*ap["diff_link"])   
    c.set_font_size(11) 
    wrapped_diff_url = textwrap.wrap(commit['diff_url'], width=(WIDTH - MARGIN * 2) // 6) 
    diff_link_y = desc_y_pos + 15
    for index, line in enumerate(wrapped_diff_url):
        c.move_to(MARGIN, diff_link_y) 
        if index == 0:
            c.show_text(f"View Diff: {line}") 
        else:
            c.show_text(line) 
        diff_link_y += 15
    
    # Hr divider
    c.set_source_rgb(*ap["text"])  
    c.set_line_width(1)  
    commit_height = get_commit_height(commit)
    divider_position = y + commit_height * 0.5
    divider_offset = commit_height * 0.38

    c.move_to(MARGIN, divider_position + divider_offset) 
    c.line_to(WIDTH - MARGIN, divider_position + divider_offset)  
    c.stroke() 

def get_commit_height(commit):  
    wrapped_desc = textwrap.wrap(commit["description"], width=(WIDTH - MARGIN * 2) // 5.5)  # Adjust divisor if needed
    return 80 + len(wrapped_desc) * 15 + 50

def draw_page_number(c, num):
    c.set_source_rgb(*ap["text"]) 
    c.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(10)
    c.move_to(MARGIN, HEIGHT - MARGIN)
    c.show_text(f"Page {num}")
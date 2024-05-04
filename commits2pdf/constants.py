import re

"""Regex for arg parser"""
DATE = re.compile((
    r"^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]"
    r"|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1"
    r"[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3"
    r"579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]"
    r"))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"
))  # d/m/yyyy or dd/mm/yyyy

EMAILS = re.compile(
    r"^([\w+-.%]+@[\w.-]+\.[A-Za-z]{2,4})(,[\w+-.%]+@[\w.-]+\.[A-Za-z]{2,4})*$"
)  # usr@email.com or usr@email.com,user2@email.com, etc

INVALID_QUERIES = re.compile(r"^,|,$")

"""Other stuff for arg parsing process"""
USAGE_INFO = (
    "Simply run ``c2p -O <owner_name>`` in the command-line to generate a PDF"
    " of your repo's commit history (assuming your current directory is a"
    " repository). Run commits2pdf -h for more information."
)
INVALID_ARG_WARNING = (
    "Invalid {} format. Run commits2pdf -h for more information."
)
CANNOT_USE_SCALE_WARNING = (
    "You cannot set scaling when using the gen1 PDF generator."
)
INVALID_BASENAME_WARNING = (
    "If the directory name of the git repository you are accessing has been"
    " renamed, there may be incorrect diff links in the output PDF."
)


"""Handling the processing of the repository"""
REPO_ALREADY_EXISTS_WARNING = (
    "The repository you are cloning from already exists, so it will be"
    " accessed normally."
)
DETACHED_BRANCH_ERROR = (
    "The repository you are cloning from already exists, but the branch you"
    " specified ({}) is detached."
)
NONEXISTING_BRANCH_WARNING = (
    "The branch you specified ({}) does not exist. Selecting the active branch"
    " ({}) instead."
)
NONEXISTING_OR_INVALID_REPO_ERROR = (
    "The repository you specified does not exist or is invalid. Attempting to"
    " delete tree..."
)
INVALID_GIT_REPO_ERROR = (
    "The path to the repo you specified ({}) does not contain a .git file."
    " Exiting..."
)
CLONING_REPO_INFO = (
    "Cloning the .git file of your specified repository. This may take a"
    " while..."
)
NONEXISTING_REPO_ERROR = (
    "The repository you specified does not exist. Exiting..."
)
MUST_RECLONE_ERROR = (
    "Please delete your repository from your file system and rerun your"
    " console command to clone a different branch of your specified"
    " repository."
)


"""Handling the filtering of the repository's commits"""
FILTER_INFO = "Filtered {} commit(s) from {} existing commit(s) based on {}."
N_COMMITS_INFO = "Selecting n {} number of commits ({})."
N_COMMITS_WARNING = (
    "{} n number of commits ({}) could not be selected as it is greater than"
    " or equal to the current amount of commits ({})."
)
GATHERED_COMMITS_INFO = (
    "Gathered {} commit(s) based on since, until and branch filters."
)


"""General PDF messages"""
WRITING_PDF_INFO = "Writing your PDF to {}"
INVALID_OUTPUT_DIR_ERROR = (
    "Your output directory is invalid. Please ensure it contains valid "
    "characters and try again."
)


"""For the pycairo PDF implementation"""
WIDTH = 612
HEIGHT = 792
MARGIN = 50


"""For the fpdf PDF implementation"""
RECURSION_ERROR = (
    "An error occured when using the gen2b renderer. Please try adding the"
    " -gen2a flag to your console command and try again."
)
CODING = "latin-1"
TITLE_FONT = ["Arial", "B", 36]
SUBTITLE_FONT = ["Arial", "", 30]
MARGIN_FONT = ["Arial", "I", 9.5]
SMALL_TEXT_FONT = ["Arial", "", 12]
MEDIUM_TEXT_FONT = ["Arial", "", 16]
TITLE_PAGE_INFO_FONT = ["Courier", "", 15]
MEDIUM_TEXT_FONT_BOLD = ["Arial", "B", 16]
INFO_TEXT_FONT = ["Courier", "", 12]
MARGIN_LR = 25.4
MARGIN_TB = 25.4


"""Appearances"""
CAIRO_LIGHT = {
    "background": (1, 1, 1),
    "text": (0, 0, 0),
    "diff_url": (0, 0, 1),
    "TYPE": "LIGHT",
}

CAIRO_DARK = {
    "background": (0.2, 0.2, 0.2),
    "text": (0.9, 0.9, 0.9),
    "diff_url": (0.6, 0.6, 1),
    "TYPE": "DARK",
}

FPDF_LIGHT = {
    "background": (255, 255, 255),
    "text": (0, 0, 0),
    "diff_url": (0, 0, 255),
    "TYPE": "LIGHT",
}

FPDF_DARK = {
    "background": (51, 51, 51),
    "text": (229, 229, 229),
    "diff_url": (123, 127, 232),
    "TYPE": "DARK",
}

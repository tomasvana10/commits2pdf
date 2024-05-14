<div align="center">

  # commits2pdf
  ![Licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
  [![PyPI version](https://img.shields.io/pypi/v/commits2pdf?style=flat-square)](https://pypi.org/project/commits2pdf/)
  [![Publish to PyPI.org](https://github.com/tomasvana10/commits2pdf/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/publish.yml)
  [![Release)](https://img.shields.io/github/v/release/tomasvana10/commits2pdf?logo=github)](https://github.com/tomasvana10/commits2pdf/releases/latest)
  [![Issues](https://img.shields.io/github/issues-raw/tomasvana10/commits2pdf.svg?maxAge=25000)](https://github.com/tomasvana10/commits2pdf/issues)
  [![CodeQL](https://github.com/tomasvana10/commits2pdf/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/github-code-scanning/codeql)
  [![Tests](https://github.com/tomasvana10/commits2pdf/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/tox-tests.yml)

</div>

Visualise a Git repository's commit history in PDF form via the command-line

![ezgif-pdf-tutorial](https://github.com/tomasvana10/commits2pdf/assets/124552709/fcc4b5da-2326-4405-80fe-cf984f61129c)

## Dependencies
`GitPython` `fpdf` `progressbar` `pathvalidate`

`pycairo` (used for deprecated PDF generation method, must be installed manually)

## Installation
**requires [pip](https://pip.pypa.io/en/stable/installation/)**

If using `python` or `pip` doesn't work, try using `python3` or `pip3`

- Make a virtual environment and activate it (recommended):
```
pip install virtualenv
python -m venv venv
MacOS/Unix: source venv/bin/activate
Windows: venv\scripts\activate
```
- Install the package in your system directory/virtual environment:
```
pip install -U commits2pdf
```
or, install the package in your home directory if you aren't using a virtual environment:
```
pip install --user -U commits2pdf
```
- You can deactivate your virtual environment when you are done:
```
deactivate
```

**If you encounter errors with building `pycairo`, click [here](https://stackoverflow.com/a/76175684/23245953)**

## Command-line parameters
```
positional arguments:
  owner                 The owner of the git repository. Required.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Directory path to your PDF output. Set to "." (your current directory) by default. Will be created if it does not exist. Example: ./work/my_pdfs
  -n NAME, --name NAME  The name of your outputted PDF file. Set to "<repo_name>-commit_report" by default.
  -b BRANCH, --branch BRANCH
                        The repository branch. Set to "main" by default.
  -a AUTHORS, --authors AUTHORS
                        Filter commits from a comma-separated list of authors. Format: <author@email.com> OR <author1@email.com,author2@email.com> etc. Set to all authors by
                        default.
  -s START_DATE, --start_date START_DATE
                        Filter from start date of commits. Format: d/m/YYYY. Example: 5/12/2023
  -e END_DATE, --end_date END_DATE
                        Filter to end date of commits. Format: d/m/YYYY. Example: 5/12/2023
  -r, --reverse         Output the commits from newest to oldest. Set to oldest to newest by default
  -d, --dark            Toggle dark mode for the output PDF. Set to "light" by default.
  -po, --prevent-open   Prevent commits2pdf from automatically opening the directory the PDF was created in.
  -sc SCALING, --scaling SCALING
                        Set the scaling of the output PDF. Only available with gen2a and gen2b.
  -in INCLUDE, --include INCLUDE
                        Include commits with the given string sequences in their title or description. Format: "<string1>" OR "<string1,string2>". Whitespace sensitive and case      
                        insensitive. NOTE: This query is performed BEFORE excluding commits.
  -ex EXCLUDE, --exclude EXCLUDE
                        Exclude commits with the given string sequences in their title or description. Format: "<string1>" OR "<string1,string2>". Whitespace sensitive and case      
                        insensitive.
  -q, --quiet           Suppress all logger messages except for errors.
  -gen1, --pdf_gen_1    PDF rendering implementation with ``pycairo``.
  -gen2a, --pdf_gen_2a  The first PDF rendering implementation with ``fpdf``.
  -gen2b, --pdf_gen_2b  The second PDF rendering implementation with ``fpdf``. The default option.
  -rp RPATH, --repo-path RPATH
                        Path to your repository directory. Set to "." (your current directory) by default.
  -fc RNAME, --repo-from-clone RNAME
                        Clone a repo into the working directory and generate the commits PDF from it automatically. Format: <repo name> (case insensitive).
  -nc NEWEST_N_COMMITS, --newest-n-commits NEWEST_N_COMMITS
                        Select the newest n number amount of commits to include after filtering.
  -oc OLDEST_N_COMMITS, --oldest-n-commits OLDEST_N_COMMITS
                        Select the oldest n number amount of commits to include after filtering.
```

## Usage
First, it is recommended that you change your terminal's directory to the path of your Git repository's folder:
- First, find your repository's folder, then:
- On Windows/Linux: Open the folder, press `CTRL+L`, then press `CTRL+C`
- On MacOS: Right click on the folder, hold `option` (`⌥`) and click `Copy <folder name> as Pathname`

Then, in your terminal, type `cd <the path you copied>` (paste in the path with `CTRL+V` or `CMD+V`). Now, you are ready to use commits2pdf!

<br>**Usage example #1**
```
c2p tomasvana10
```
> Output a PDF to your current directory (assuming it is a git repository that is owned by `tomasvana10`).

<br>**Usage example #2**
```
c2p tomasvana10 -o .. -rp ./my_repo -n "new_name.pdf"
```
> Output a PDF (overriding its name to `new_name`) to the parent directory, selecting `./my_repo` as your git repository to access the commits from.

<br>**Usage example #3**
```
c2p tomasvana10 -nc 10 -in "javascript,build" -ex "testing"
```
> Output a PDF to the current directory, displaying the newest 10 commits after filtering commits that contain "javascript" and/or "build in their title or description and do not contain "testing".

<br>**Usage example #4**
```
c2p devguarv -fc Yr-12-HSC-SDD-Task-2 -e 28/4/2024
```
> Clone the repo `Yr-12-HSC-SDD-Task-2` into the current directory and output a PDF into the same place after filtering commits that were made up to `28/4/2024`.

## PDF generation implementations
### pycairo (gen1 - deprecated)
👍 Fast<br>
👎 Cannot write multipage commits<br>
👎 Looks like crap<br>
👎 No hyperlinks, therefore the entire link to a commit's diff is displayed

### fpdf (gen2a)
👍 Fast<br>
👍 Can be scaled with the `-sc <float>` argument<br> 
👍 Sleek design<br>
👍 Information title page<br>
👍 Contains hyperlinks<br>
👍 Stores PDF metadata<br>
👎 Inconsistent page breaks, a general limitation with FPDF when trying to fit as many whole commits on a single page<br> 

### fpdf (gen2b - Default)
👍 Same as `gen2a` but with accurate page breaking<br>
👎 Slow when generating large amounts of commits (generally, it is a good idea to enable `-gen2a` when drawing over 5000 commits)<br>

![Licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
[![PyPI version](https://img.shields.io/pypi/v/commits2pdf?style=flat-square)](https://pypi.org/project/commits2pdf/)
[![Publish to PyPI.org](https://github.com/tomasvana10/commits2pdf/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/publish.yml)
[![Release)](https://img.shields.io/github/v/release/tomasvana10/commits2pdf?logo=github)](https://github.com/tomasvana10/commits2pdf/releases/latest)
[![Issues](https://img.shields.io/github/issues-raw/tomasvana10/commits2pdf.svg?maxAge=25000)](https://github.com/tomasvana10/commits2pdf/issues)
[![CodeQL](https://github.com/tomasvana10/commits2pdf/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/github-code-scanning/codeql)
[![Tests](https://github.com/tomasvana10/commits2pdf/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/commits2pdf/actions/workflows/tox-tests.yml)

# commits2pdf
Visualise a GitHub repository's commit history in PDF form via the command-line
<br><br>
## Dependencies
`pycairo`<br>
`GitPython`<br>
`fpdf`<br>
`progressbar`
<br><br>
## Installation
**Requires [pip](https://pip.pypa.io/en/stable/installation/)**

Make a virtual environment (recommended)
```
pip install virtualenv OR pip3 install virtualenv
python -m venv venv OR python3 -m venv venv
ON MACOS/UNIX: source venv/bin/activate
ON WINDOWS: venv\scripts\activate
```

Install the package in your system directory/virtual environment:
```
pip install -U commits2pdf OR pip3 install -U commits2pdf
```
OR, install the package in your home directory (good if you aren't using a virtual environment):
```
pip install --user -U commits2pdf
```


**If you encounter errors with building `pycairo`, click [here](https://stackoverflow.com/a/76175684/23245953)**
<br><br>
## Command-line parameters
```
positional arguments:
  owner                 The owner of the git repository. Required.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Directory path to your PDF output. Set to "." by default. Will be created if it does not exist. Example: -o ./work/my_pdfs
  -b BRANCH, --branch BRANCH
                        The repository branch. Set to "main" by default.
  -a AUTHORS, --authors AUTHORS
                        Filter commits from a comma-separated list of authors. Format: <author@email.com> OR <author1@email.com,author2@email.com> etc. Set to all authors by
                        default.
  -s START_DATE, --start_date START_DATE
                        Filter from start date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05
  -e END_DATE, --end_date END_DATE
                        Filter to end date of commits. Format: YYYY-mm-dd or YYYY-m-d. Example: 2023-12-05
  -r, --reverse         Output the commits from newest to oldest. Set to oldest to newest by default
  -d, --dark            Toggle dark mode for the output PDF. Set to "light" by default.
  -po, --prevent-open   Prevent commits2pdf from automatically opening the directory the PDF was created in.
  -sc SCALING, --scaling SCALING
                        Set the scaling of the output PDF. Only available with gen2a and gen2b.
  -gen1, --pdf_gen_1    PDF rendering implementation with ``pycairo``.
  -gen2a, --pdf_gen_2a  The first PDF rendering implementation with ``fpdf``.
  -gen2b, --pdf_gen_2b  The second PDF rendering implementation with ``pycairo``. The default option.
  -qa QUERIES_ANY, --query-any QUERIES_ANY
                        Select the commits whose title OR description match ANY part of your query. Format: "<query1>" OR "<query1,query2>" etc. Note: queries can have leading or    
                        trailing whitespace.
  -QA QUERIES_ALL, --query-all QUERIES_ALL
                        Select the commits whose title OR description match ALL parts of your query. Format: "<query1>" OR "<query1,query2>" etc. Note: queries can have leading or   
                        trailing whitespace.
  -rp RPATH, --repo-path RPATH
                        Path to your repository directory. Set to "." by default.
  -fc RNAME, --repo-from-clone RNAME
                        Clone a repo into the working directory and generate the commits PDF from it automatically. Format: <repo name> (case insensitive).
  -nnc NEWEST_N_COMMITS, --newest-n-commits NEWEST_N_COMMITS
                        Select the newest n number amount of commits to include after filtering.
  -onc OLDEST_N_COMMITS, --oldest-n-commits OLDEST_N_COMMITS
                        Select the oldest n number amount of commits to include after filtering.
```
<br>

## Usage
<br>**Simple usage - what you will be using the most**:
```
c2p tomasvana10
```
_Explanation_: Run the CLI tool in the current directory (assuming it is a Git repository). The owner name must be provided in all cases.

<br>**Advanced usage example #1**:
```
c2p tomasvana10 -rp ../seriescalculator_sdd -a person@email.com,other_person@gmail.com -s 2024-11-30 -e 2024-12-30 -b other_branch -d
```
_Explanation_: 
1. Override the default repository path (``-rp ..\seriescalculator_sdd``) with a folder in the parent directory.
2. Look for specific commit emails (separated by commas)
3. Search for commits from the -s date until the -e date
4. Search for commits only made to `other_branch`
5. Toggle dark mode for the PDF output

<br>**Advanced usage example #2**
```
c2p tomasvana10 -nnc 10 -r
```
_Explanation_: Display the newest ten commits (after any filtering) in reverse order (newest to oldest instead of the default, which is oldest to newest).

<br>**Advanced usage example #3**
```
c2p tomasvana10 -qa "javascript,test " -onc 5 -po -o ..
```
_Explanation_: 
1. Display the 5 oldest commits after querying the current repository's commits for either "javascript" OR "test "
2. Prevent the PDF directory from being automatically opened.
3. Output the PDF to the parent directory (`..`)

**NOTE**: -qa selects commits that include **any** query criteria in the title **OR** description, while -QA selects commits that include **ALL** query criteria in the title or description.

<br>**Advanced usage example #4**
```
c2p tomasvana10 -QA "dev ,testing" -gen2a -sc 0.8
```
_Explanation_:
1. Query the repo for both "dev " AND "testing"
2. Use the `gen2a` PDF renderer to visualise the PDF
3. Set the scaling of the PDF output to 0.8

**NOTE**: Scaling (`-sc`) is only available when using `gen2a` or `gen2b`. `gen2b` is default.

<br>**Clone the repo you want to document on-demand**:
```
c2p tomasvana10 -fc some_repo_name
```
_Explanation_: Create the repo you have specified and make the PDF. This repo is always cloned into the current working directory.
<br><br>
## PDF Generation implementations
### pycairo (gen1)
+ Fast
- Looks like crap 
- No hyperlinks, therefore the entire link to a commit's diff is displayed
- Occasional bugs in rendering

### fpdf (gen2a)
+ Fast
+ Can be scaled with the `-sc <float>` argument 
+ Sleek design
+ Information title page
+ Contains hyperlinks
+ Stores PDF metadata
- Inconsistent page breaks, a general limitation with FPDF when trying to fit as many whole commits on a single page 

### fpdf (gen2b - Default)
+ Same as gen2a but with perfectly accurate page breaking
- Slow when generating large amounts of commits (generally, it is a good idea to switch to gen2a when drawing over 5000 commits)

<br><br>
## Gallery
**gen1 title page**<br>
<img src="https://github.com/tomasvana10/commits2pdf/assets/124552709/b243e102-0eda-4750-bbce-027f5738405b" alt="gen1 pdf title page" width=561.12>

**gen2 title page in dark mode**<br>
<img src="https://github.com/tomasvana10/commits2pdf/assets/124552709/e1f2fe53-1c72-42a6-a89b-44a27c0b06a9" alt="gen2 pdf title page dark" width=561.12>

**gen2 commit page in dark mode**<br>
<img src="https://github.com/tomasvana10/commits2pdf/assets/124552709/a9fd3341-e661-4355-91e7-0dc3182e7239" alt="gen2 pdf commit page dark" width=561.12>

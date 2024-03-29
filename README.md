# commits2pdf
Visualise a GitHub repo's commit history in PDF form via the command-line
<br><br>
## Dependencies
`pycairo`<br>
`GitPython`
<br><br>
## Installation
`pip install commits2pdf` or<br>
`pip3 install commits2pdf`
<br><br>
## Usage
**Simple usage**:
```
commits2pdf -ow tomasvana10
```
_Explanation_: Run the commmits2pdf cli tool in the current directory (assuming it is a repository). The owner name must be provided in all cases.

<br>**More advanced usage**:
```
commits2pdf -ow tomasvana10 -rp ../seriescalculator_sdd -a person@email.com,other_person@gmail.com -s 2024/11/30 -e 2024/12/30 -b other_branch -l
```
_Explanation_: 
1. Override the default repository path
2. Look for specific commit emails (separated by commas)
3. Search for commits from the -s value until the -e value
4. Search for commits only made to `other_branch`
5. Toggle light mode for the PDF output (`-l`)

<br>**Clone the repo you need on-demand**:
```
commits2pdf -ow tomasvana10 -fc some_repo_name
```
_Explanation_: Create the repo you have specified and make the PDF (in the current working directory, not the new repo directory). A path for this repo can be specified using the `-rp` parameter.

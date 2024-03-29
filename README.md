# commits2pdf
Visualise a GitHub repo's commit history in PDF form via the command-line
<br><br>
## Dependencies
`pycairo`<br>
`GitPython`
<br><br>
## Installation
`pip install commits2pdf` or<br>
`pip3 install commits2pdf`<br>
If you encounter errors with building `pycairo`, click [here](https://stackoverflow.com/a/76175684/23245953)
<br><br>
## Usage
**Simple usage**:
```
commits2pdf -o tomasvana10
```
_Explanation_: Run the commmits2pdf cli tool in the current directory (assuming it is a repository). The owner name must be provided in all cases.

<br>**Advanced usage example #1**:
```
commits2pdf -o tomasvana10 -rp ../seriescalculator_sdd -a person@email.com,other_person@gmail.com -s 2024/11/30 -e 2024/12/30 -b other_branch -l
```
_Explanation_: 
1. Override the default repository path
2. Look for specific commit emails (separated by commas)
3. Search for commits from the -s value until the -e value
4. Search for commits only made to `other_branch`
5. Toggle light mode for the PDF output (`-l`)

<br>**Advanced usage example #2**
```
commits2pdf -o tomasvana10 -nnc 10 -r
```
_Explanation_: Display the newest ten commits (after any filtering) in reverse order (newest to oldest instead of the default, which is oldest to newest).

<br>**Clone the repo you want to document on-demand**:
```
commits2pdf -o tomasvana10 -fc some_repo_name
```
_Explanation_: Create the repo you have specified and make the PDF (in the current working directory, not the new repo directory). This repo is always cloned into the current working directory.
<br><br>
## Gallery
<img width="513" alt="commits pdf dark" src="https://github.com/tomasvana10/commits2pdf/assets/124552709/40d88bfc-c727-425a-9b7e-74da89c52220"> 
<hr>
<img width="509" alt="commits pdf light" src="https://github.com/tomasvana10/commits2pdf/assets/124552709/1ec90e60-53fa-41b1-a816-8e420ecb3c9a">
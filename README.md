# printRandomExamQuestions

Script that takes questions and their espective answers from a Google Speadsheet, choose a random number of questions among the question set for a given number of files. Then, the script compiles each file using [XeTex](https://en.wikipedia.org/wiki/XeTeX), aggregates the resuilting pdf file in a master pdf file (`exam.pdf`) and print the master pdf file using CUPS.

Here is the pipeline of the script:

![Pipeline](https://docs.google.com/drawings/d/1VqeIC7rApha38_vspmRhC1zaD0GFc_--1UgqMhjP92Y/pub?w=853&h=237)

## Dependencies:

 - [`cups`](https://pypi.python.org/pypi/pycups)
 - [`pyPdf`](http://stackoverflow.com/questions/3444645/merge-pdf-files)
 - [`gspread`](http://gspread.readthedocs.org/en/latest/index.html)
 - [XeTex](https://en.wikipedia.org/wiki/XeTeX)

When you try to execute the `xelatex` command, make sure you have the `xelatex` binary executable in the `PATH`:
`export PATH=/usr/local/texlive/2014/bin/x86_64-darwin/:$PATH`

Also, you need to follow [these instructions](http://gspread.readthedocs.org/en/latest/oauth2.html#custom-credentials-objects) to enable the access of the Google SpreadSheet. Then, make sure you have shared the Google SpreadSheet with the email address given in the `PrintQuestions-***.json`

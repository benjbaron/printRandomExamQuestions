#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cups
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import random
import subprocess
import io
import sys
import optparse
from pyPdf import PdfFileWriter, PdfFileReader


# CUPS: look for printer: http://localhost:631/jobs/

reload(sys)
sys.setdefaultencoding("utf-8")

# Need to update the path for xeLatex
# export PATH=/usr/local/texlive/2014/bin/x86_64-darwin/:$PATH
PREAMBULE_FILE = "preambule.tex"
PRINTER_NAME = "Cristal___Imprimante_NPA__Noir_et_Blanc____hera_lip6_fr"
TMP_LATEX_FILE = "tmp"
TMP_LATEX_FILE_COR = "tmp_cor"
OUTPUT_FILE = "exam.pdf"


def generate_latex_preambule(date, answers):
    """
    :param date: date of the exam
    :return: the resulting text file
    """
    if answers:
        print_answer = "\printanswers"
    else:
        print_answer = ""

    str = """\input{{{preambule}}}

{print_answer}

\\begin{{document}}

\pagestyle{{headandfoot}}
\\firstpageheader{{}}{{}}{{}}
\\runningheader{{\\textsf{{\\textbf{{LI320}} Évaluation}}}}{{}}{{\\fbox{{\parbox[c][2em][c]{{6cm}}{{Nom : }} }}}}
\\firstpagefooter{{}}{{\\thepage\ sur \\numpages}}{{}}
\\runningfooter{{}}{{\\thepage\ sur \\numpages}}{{}}

{{\Huge \\textsf{{\\textbf{{3I 023}} Ingénierie des réseaux}}\\\\[15pt]}}%
\\begin{{minipage}}{{.59\linewidth}}
\\begin{{flushleft}}\leavevmode
    {{\Large \\textsf{{Évaluation}}\\\\[2pt]}}%
    {{\large \\textbf{{\\textit{{{date}}}}}}}%
\end{{flushleft}}%
\end{{minipage}}
\hfill
\\begin{{minipage}}{{.4\linewidth}}
\\begin{{flushright}}
\\fbox{{\parbox[c][2.5em][c]{{6cm}}{{Nom :\\\\Numéro d'étudiant :}}}}
\end{{flushright}}
\end{{minipage}}

\\vspace*{{15pt}}
    """.format(preambule=PREAMBULE_FILE, date=date, print_answer=print_answer)

    return str.decode('utf-8')


def generate_latex_file(output, questions, print_answers, exam_date):
    """
    Generate the latex file from the questions and the answers lists.
    If the answers list is empty, then do not print the answers
    :param output: output filename
    :param questions: list of questions
    :param answers: list of answers to the questions (may be empty)
    :param print_answers: whether to print the answers or not
    """

    f = io.open(output, 'w', encoding='utf8')
    # Copy the preambule in the output file
    f.write(generate_latex_preambule(exam_date, print_answers))

    f.write(u"\\begin{questions}\n")
    # print the questions
    for i in range(len(questions)):
        question_cours = '(Cours) ' if questions[i]['c'] else ''
        str = u"""
    \\question {question_cours}
    {question}
    \\begin{{solutionordottedlines}}[0.55in]
        {answer}
    \\end{{solutionordottedlines}}
""".format(question_cours=question_cours,question=questions[i]['q'], answer=questions[i]['a'])
        f.write(unicode(str))
    f.write(u"\\end{questions}\n\n\\end{document}")


def get_questions(sheet_idx):
    # Need to add the right credentials:
    # See: http://gspread.readthedocs.org/en/latest/oauth2.html#custom-credentials-objects

    print "Getting questions..."
    # authentication
    json_key = json.load(open('PrintQuestions-8a4381f64e79.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    sheet_key = "1u_nkgY15ACvp2fUCZPMiQOt0ft5yFN5WK-FHpGF_YCA"

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

    gc = gspread.authorize(credentials)

    wks = gc.open_by_key(sheet_key).get_worksheet(int(sheet_idx)-1)

    records = []
    for (i, v) in enumerate(wks.get_all_values()[1:]):
        if v:
            records.append({
                'q': v[0],
                'a': v[3],
                'td': v[2],
                'c': True if v[1] == '1' else False
            })

    return records

def choose_questions(nrof_questions, nrof_exams, td_group, records):
    # Choose the questions to include in the file
    questions_results = {}
    for i in range(int(nrof_exams)):
        questions_results[i] = []
        question_set = set(dict(enumerate(rec for rec in records if rec['td'] in [td_group,''])).keys())
        for j in range(int(nrof_questions)):
            # get a random question
            q = random.choice(list(question_set))

            # remove the question from the question set
            question_set.remove(q)

            # add the question to the resulting question set
            questions_results[i].append(q)

    return questions_results


def compile_latex_file(filename):
    print filename
    subprocess.call("xelatex %s" % filename, shell=True)
    subprocess.call("xelatex %s" % filename, shell=True)


def print_file(filename):
    print "[Printing file " + filename + "]"
    conn = cups.Connection()
    printer_returns = conn.printFile(PRINTER_NAME, filename, 'test', {})
    print printer_returns


def get_options():
    optParser = optparse.OptionParser()

    optParser.add_option("-c",  action="store", dest='course_number', help="Number of the course")
    optParser.add_option("-d",  action="store", dest='date', help='Date of the exam')
    optParser.add_option("-n",  action="store", dest='exam_number', help='Number of exams')
    optParser.add_option("-q",  action="store", dest='questions_number', help='Number of questions')
    optParser.add_option("-t",  action="store", dest='td_group', help='TD group')

    options, args = optParser.parse_args()
    return options


def remove_latex_files(filename):
    try:
        os.remove(filename+".aux")
        os.remove(filename+".log")
        os.remove(filename+".out")
        os.remove(filename+".pdf")
        os.remove(filename+".tex")
    except OSError:
        pass


def append_pdf(input, output):
    [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]


def main():
    options = get_options()

    sheet_idx   = options.course_number
    date_exam   = options.date
    exam_number = options.exam_number
    questions_number = options.questions_number
    td_group = options.td_group

    output = PdfFileWriter()

    records = get_questions(sheet_idx)
    res = choose_questions(questions_number, exam_number, td_group, records)

    for i, questions_idx in res.items():
        questions = [records[idx] for idx in questions_idx]
        generate_latex_file(TMP_LATEX_FILE+".tex", questions, False, date_exam)
        compile_latex_file(TMP_LATEX_FILE+".tex")
        append_pdf(PdfFileReader(file(TMP_LATEX_FILE+".pdf", "rb")), output)

        # Remove the temporary files
        remove_latex_files(TMP_LATEX_FILE)

    output.write(file(OUTPUT_FILE, "wb"))
    # print_file(OUTPUT_FILE)



if __name__ == '__main__':
    main()

# run the command
# export PATH=/usr/local/texlive/2014/bin/x86_64-darwin/:$PATH
# python printQuestions.py -c 1 -n 3 -q 10 -d "Semaine du 3 février"

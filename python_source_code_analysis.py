#!/usr/bin/python3

import os
import re
from pylint import epylint as lint
from io import StringIO
from rich import print
from rich.console import Console
from rich.table import Table

# TODO: doc


def python_code_analysis(file_name, file_path, dataset_candidates, verbose):
    f_name = file_name
    file_directory = get_file_directory(file_path)
    os.chdir(file_directory)
    is_jupyter_notebook = 0

    if '.ipynb' in file_name:
        f_name = convert_jupyter_nb_to_py(file_name)
        is_jupyter_notebook = 1

    file = file_directory + '/' + f_name

    source_code = open(file, "r")
    sc_lines = source_code.readlines()
    source_code.close()

    comment_lines = []
    code_lines = []
    import_lines = []
    mentioned_dataset_candidates = []

    # TODO: Strategy how to evaluate header + footer further?
    # NOTE COMMENT LINES BEFORE FIRST CODE LINE
    header_comment = 0
    header_comment_present = 'true'
    header_comments = []

    # NOTE COMMENT LINES AFTER THE LAST PIECE OF CODE
    footer_comment = 0
    footer_comments = []

    fixed_random_seed_lines = []
    unfixed_random_seed_lines = []

    for l in sc_lines:
        if not l.isspace():
            line = l.strip()
            if line[:1] == '#':
                comment = parse_comment_line(line)
                if comment:
                    comment_lines.append(comment)

                    if header_comment_present == 'true':
                        header_comments.append(comment)

                    footer_comments.append(comment)
            elif line.split()[0] in ('from', 'import'):
                imp = parse_import_line(line)
                if imp:
                    if imp not in import_lines:
                        import_lines.append(imp)
            else:
                code_line = parse_code_line(line)
                random_seed_line = check_for_random_seed(code_line)

                if random_seed_line == 1:
                    fixed_random_seed_lines.append(code_line)

                if random_seed_line == 2:
                    unfixed_random_seed_lines.append(code_line)

                # check if one of the dataset candidates is mentioned in this line of code
                mentioned_dataset_candidates = check_dataset_candidates(code_line, dataset_candidates,
                                                                        mentioned_dataset_candidates)
                code_lines.append(code_line)
                header_comment_present = 'processed'
                if footer_comments:
                    footer_comments.clear()

    if header_comments:
        header_comment = len(header_comments)

    if footer_comments:
        footer_comment = len(footer_comments)

    hp_import_indicators = check_import_hyperparameter_indicators(import_lines)
    hp_code_indicators = check_code_hyperparameter_indicators(code_lines)

    number_of_hp_doc_indicator = len(hp_import_indicators) + len(hp_code_indicators)

    pylint_rating = pylint_code_style_rating(f_name, file, verbose)

    number_of_comment_lines = len(comment_lines)
    number_of_code_lines = len(code_lines) + len(import_lines)
    total_sc_lines = number_of_comment_lines + number_of_code_lines

    number_of_fixed_random_seed_lines = len(fixed_random_seed_lines)
    number_of_random_seed_lines = number_of_fixed_random_seed_lines + len(unfixed_random_seed_lines)

    if verbose == 1:
        build_feedback(code_lines, comment_lines, import_lines, number_of_code_lines, number_of_comment_lines,
                       f_name, file, pylint_rating, fixed_random_seed_lines, unfixed_random_seed_lines,
                       hp_import_indicators, hp_code_indicators)

    return [number_of_code_lines, number_of_comment_lines, pylint_rating, total_sc_lines, header_comment,
            footer_comment, is_jupyter_notebook, number_of_random_seed_lines, number_of_fixed_random_seed_lines,
            number_of_hp_doc_indicator, import_lines, mentioned_dataset_candidates]


# removing file name
def get_file_directory(file_path):
    idx = file_path.rfind("/")
    if idx >= 0:
        file_path = file_path[:idx]
    return file_path


def convert_jupyter_nb_to_py(file_name):
    f_name = re.sub(r"[^a-zA-Z0-9.]", "", file_name)
    os.rename(file_name, f_name)
    os.system('jupyter nbconvert --to script ' + str(f_name) + ' --to python')
    f_name = f_name.replace('.ipynb', '.py')
    return f_name


def parse_comment_line(comment_line):
    # jupyter notebook artefact, not an actual comment
    if '# In[' in comment_line:
        return
    if '!/usr/bin/env' in comment_line:
        return

    comment = comment_line.replace('#', '')
    comment = comment.replace('\n', '')
    return remove_leading_whitespace(comment)


def parse_import_line(import_line):
    imp = remove_leading_whitespace(import_line).split()[1]

    # TODO: solution
    # problem: from . import (xy, xy, xy)

    if '.' in imp and not imp.startswith('.'):
        imp = imp.split('.')[0]
    return imp


def parse_code_line(code_line):
    code = remove_leading_whitespace(code_line)
    return code.replace('\n', '')


# returns 1 if random seed found + value fixed
# returns 2 if random seed found but no value fixed
# otherwise 0
def check_for_random_seed(code_line):
    # 'random + wildcard + ='
    reg_random = re.compile("random.+?=")
    # 'xy_seed_xy ='
    reg_seed = re.compile("(.+)?seed.+?=")

    code_line = code_line.lower().replace(',', '')
    code_line_replaced = code_line.replace('(', ' ')
    code = code_line_replaced.split()

    # check for random seed and random state method
    if 'seed(' in code_line:
        if 'seed()' not in code_line:
            return 1
        else:
            return 2

    elif '.randomstate(' in code_line:
        if '.randomstate()' not in code_line:
            return 1
        else:
            return 2

    elif bool(re.match(reg_seed, code_line)):
        return 1

    else:
        # checking for declaration inside method call
        for word in code:
            if bool(re.match(reg_random, word)):
                return 1

    return 0


def check_dataset_candidates(code_line, dataset_candidates, mentioned_dataset_candidates):
    for candidate in dataset_candidates:
        if candidate in code_line:
            if candidate not in mentioned_dataset_candidates:
                mentioned_dataset_candidates.append(candidate)

    return mentioned_dataset_candidates


# checking for hyperparameter logging relevant libraries and code lines
# atm just checking existence not quality or quantity
def check_import_hyperparameter_indicators(imp_lines):
    # checking for wandb, neptune, sacred and kubeflow imports
    # these imports enable hyperparameter logging, exporting, etc.
    hp_relevant_imports = []

    for imp_line in imp_lines:
        if imp_line not in hp_relevant_imports:
            if 'wandb' in imp_line:
                hp_relevant_imports.append(imp_line)
            if 'neptune' in imp_line:
                hp_relevant_imports.append(imp_line)
            if 'kubeflow' in imp_line:
                hp_relevant_imports.append(imp_line)
            if 'sacred' in imp_line:
                hp_relevant_imports.append(imp_line)

    return hp_relevant_imports


def check_code_hyperparameter_indicators(code_lines):
    # searching for mlflow.xy.autolog() or mlflow.log in source code
    hp_relevant_code = []

    reg = re.compile("mlflow.+?log")
    for code_line in code_lines:
        if bool(re.match(reg, code_line)):
            hp_relevant_code.append([code_line])

    return hp_relevant_code


def pylint_code_style_rating(file, file_path, verbose):
    # ignoring "Unable to import '<library>' (import-error)"
    file_tmp = file
    if ' ' in file:
        file_tmp = file.replace(' ', '\ ')
    (pylint_stdout, pylint_stderr) = lint.py_run(file_tmp + ' --disable E0401', return_std=True)
    stdout = StringIO.getvalue(pylint_stdout).splitlines()
    stderr = StringIO.getvalue(pylint_stderr).splitlines()

    # print additional information to console if verbose mode
    if verbose == 1:
        print('\n:crossed_fingers: [bold magenta] Result of pylint analysis of ' + file + '. Path to file: '
              + file_path + '[/bold magenta]\n')
        print(stdout)
        if stderr:
            print(stderr)

    # 3rd last element of stdout is the string with the rating result
    # returns retrieved pylint rating (ranging from -10 to 10)
    if stdout:
        rating_sentence = (stdout[-3])
        rs_list = rating_sentence.split()
        if len(rs_list) >= 7:
            return float(rs_list[6].split('/')[0])
        return 0
    # if no rating
    else:
        return 0


def remove_leading_whitespace(line):
    return re.sub(r"^\s+", "", line)


def build_feedback(code_lines, comment_lines, imp_lines, number_of_code_lines, number_of_comment_lines,
                   file_name, file_path, pylint_rating, fixed_rdm_seed_lines, unfixed_rdm_seed_lines,
                   hp_import_indicators, hp_code_indicators):
    # > 1 means there is more code lines than comment lines
    if number_of_comment_lines > 0:
        code_comment_ratio = round(number_of_code_lines / number_of_comment_lines, 2)
    else:
        code_comment_ratio = number_of_code_lines
    console = Console()

    print('\n:detective: [bold magenta] Result of source code analysis of ' + file_name + '. Path to file: '
          + file_path + '[/bold magenta]\n')
    print('[bold red]SOURCE CODE ANALYSIS FOR FILE: ' + file_name + '[/bold red]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# code lines:', str(number_of_code_lines))
    table.add_row('# comment lines', str(number_of_comment_lines))
    table.add_row('Code-comment-ratio', str(code_comment_ratio))
    table.add_row('Pylint rating', str(pylint_rating))
    console.print(table)
    print('\n')

    # print additional information to console if verbose mode
    if code_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("SOURCE CODE LINES", justify="left")
        for code_line in code_lines:
            table.add_row(code_line)
        console.print(table)
        print('\n')

    if comment_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("SOURCE CODE COMMENTS", justify="left")
        for comment in comment_lines:
            table.add_row(comment)
        console.print(table, markup=False)
        print('\n')

    if imp_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("SOURCE CODE IMPORTS", justify="left")
        for import_line in imp_lines:
            table.add_row(import_line)
        console.print(table)
        print('\n')

    if fixed_rdm_seed_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("FIXED RANDOM SEED LINES", justify="left")
        for line in fixed_rdm_seed_lines:
            table.add_row(line)
        console.print(table)
        print('\n')

    if unfixed_rdm_seed_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("UNFIXED RANDOM SEED LINES", justify="left")
        for line in unfixed_rdm_seed_lines:
            table.add_row(line)
        console.print(table)
        print('\n')

    if hp_import_indicators:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("INDICATORS OF HYPERPARAMETER DOCUMENTATION: IMPORT LINES", justify="left")
        for indicator in hp_import_indicators:
            table.add_row(indicator)
        console.print(table)
        print('\n')

    if hp_code_indicators:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("INDICATORS OF HYPERPARAMETER DOCUMENTATION: CODE LINES", justify="left")
        for indicator in hp_code_indicators:
            table.add_row(indicator)
        console.print(table)
        print('\n')

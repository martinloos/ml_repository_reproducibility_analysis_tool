#!/usr/bin/python3

import filter_repository_artefacts
import python_source_code_analysis
from rich import print
from rich.console import Console
from rich.table import Table
import logging

import dataset_analysis

logger = logging.getLogger('log')
source_code_file_results = []
source_code_analysis_result = []
unique_imports = []
mentioned_dataset_files = []

# TODO: doc

# Analysing the source code of the repository
# We only accept python code (and Jupyter Notebooks) at the moment
# Other source code types can be integrated here


def analyze_source_code(verbose):
    source_code_files = filter_repository_artefacts.get_source_code_files()
    dataset_file_candidates = dataset_analysis.get_dataset_file_candidates()
    counter = 1

    for file in source_code_files:
        file_name = file[0]
        file_path = file[1]
        logger.info('Processing source code file ' + str(counter) + ' out of ' + str(len(source_code_files))
                    + ' (' + file_name + ')')
        # add other elif clause to support other source code types
        if 'py' in file_name:
            sc_analysis_result = python_source_code_analysis.python_code_analysis(file_name, file_path,
                                                                                  dataset_file_candidates, verbose)
            source_code_file_results.append(sc_analysis_result)
        counter = counter + 1

    build_source_code_result()


def get_file_length(file_path):
    i = 0
    with open(file_path) as r:
        for i, l in enumerate(r):
            pass
    return i + 1


def get_source_code_analysis():
    return source_code_analysis_result


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def check_for_dvc():
    dvc_folder = filter_repository_artefacts.get_dvc_folder()
    if dvc_folder:
        return 1


def get_imports():
    return unique_imports


def get_mentioned_dataset_files():
    return mentioned_dataset_files


def build_source_code_result():
    number_of_sc_files = len(source_code_file_results)
    total_code_lines = 0
    total_comment_lines = 0
    weighted_pylint_sum = 0
    total_sc_lines = 0
    number_of_jn = 0
    jn_with_header_comment = 0
    jn_with_footer_comment = 0
    number_of_rdm_seed_lines = 0
    number_of_fixed_rdm_seed_lines = 0
    number_of_hyperparameter_doc_indicators = 0

    for result in source_code_file_results:
        total_code_lines = total_code_lines + result[0]
        total_comment_lines = total_comment_lines + result[1]
        total_sc_lines = total_sc_lines + result[3]
        # weighted pylint result (depending on source code lines of file)
        weighted_pylint_sum = weighted_pylint_sum + result[2] * result[3]
        # analyzed source code file was .ipynb file
        if result[6] == 1:
            number_of_jn = number_of_jn + 1
            # .ipynb had header comments
            if not result[4] == 0:
                jn_with_header_comment = jn_with_header_comment + 1
            # .ipynb had footer comments
            if not result[5] == 0:
                jn_with_footer_comment = jn_with_footer_comment + 1
        number_of_rdm_seed_lines = number_of_rdm_seed_lines + result[7]
        number_of_fixed_rdm_seed_lines = number_of_fixed_rdm_seed_lines + result[8]
        number_of_hyperparameter_doc_indicators = number_of_hyperparameter_doc_indicators + result[9]

        for imp in result[10]:
            if imp not in unique_imports:
                unique_imports.append(imp)

        for dataset_file in result[11]:
            if dataset_file not in mentioned_dataset_files:
                mentioned_dataset_files.append(dataset_file)

    percentage_code_lines = calculate_percentage(total_code_lines, total_sc_lines)
    percentage_comment_lines = calculate_percentage(total_comment_lines, total_sc_lines)
    average_pylint_score = round(weighted_pylint_sum / total_sc_lines, 2)

    # > 1 means there is more code lines than comment lines
    if total_comment_lines > 0:
        code_comment_ratio = round(total_code_lines / total_comment_lines, 2)
    else:
        code_comment_ratio = total_code_lines

    average_jn_header_comment = 0
    average_jn_footer_comment = 0

    if number_of_jn > 0:
        average_jn_header_comment = calculate_percentage(jn_with_header_comment, number_of_jn)
        average_jn_footer_comment = calculate_percentage(jn_with_footer_comment, number_of_jn)

    percentage_fixed_rdm_seed = 0

    if number_of_rdm_seed_lines > 0:
        percentage_fixed_rdm_seed = calculate_percentage(number_of_fixed_rdm_seed_lines, number_of_rdm_seed_lines)

    dvc_used = 'No'
    # data version control -> number of hyperparameter indicators irrelevant because models are versioned
    if check_for_dvc() == 1:
        dvc_used = 'Yes'

    source_code_analysis_result.extend((number_of_sc_files, total_code_lines, percentage_code_lines,
                                        total_comment_lines, percentage_comment_lines, code_comment_ratio,
                                        average_pylint_score, number_of_jn, average_jn_header_comment,
                                        average_jn_footer_comment, number_of_rdm_seed_lines, percentage_fixed_rdm_seed,
                                        dvc_used, number_of_hyperparameter_doc_indicators))

    console = Console()

    print('\n\n')
    print('[bold] _______________________________________________________[/bold]')
    print('[bold]|[magenta]                   SOURCE CODE ANALYSIS                [/magenta]|[/bold]')
    print('[bold]|_______________________________________________________|[/bold]\n')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# source code files', str(number_of_sc_files))
    table.add_row('# total lines of code', str(total_code_lines))
    table.add_row('% of code lines', str(percentage_code_lines))
    table.add_row('# total comment lines', str(total_comment_lines))
    table.add_row('% of comment lines', str(percentage_comment_lines))
    table.add_row('code-comment-ratio', str(code_comment_ratio))
    table.add_row('average pylint score (best is 10)', str(average_pylint_score))
    table.add_row('# jupyter notebooks', str(number_of_jn))
    table.add_row('% of jupyter notebooks /w header', str(average_jn_header_comment))
    table.add_row('% of jupyter notebooks /w footer', str(average_jn_footer_comment))
    table.add_row('# random seed lines', str(number_of_rdm_seed_lines))
    table.add_row('% fixed random seed lines', str(percentage_fixed_rdm_seed))
    table.add_row('Data version control used?', dvc_used)
    table.add_row('# hyperparameter documentation indicators', str(number_of_hyperparameter_doc_indicators))
    console.print(table)
    print('\n')

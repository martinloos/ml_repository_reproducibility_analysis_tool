#!/usr/bin/python3

import csv
import os
from rich import print
from rich.console import Console
from rich.table import Table

from modules import readme_analysis, license_analysis, dataset_analysis, source_code_analysis, config_files_analysis, \
    binderhub_call

# TODO: doc
# Builds result with retrieved data
# Stores result in file

analysis_result = []


def get_analysis_result():
    return analysis_result


def build_result(repository_url, output_file):

    readme_result = readme_analysis.get_readme_analysis()
    if not readme_result:
        readme_result = build_zero_value_list(7)

    license_result = license_analysis.get_license_result()
    if not license_result:
        license_result = build_zero_value_list(3)

    source_code_result = source_code_analysis.get_source_code_analysis()
    if not source_code_result:
        source_code_result = build_zero_value_list(15)

    config_analysis = config_files_analysis.get_config_analysis_result()
    if not config_analysis:
        config_analysis = build_zero_value_list(7)

    dataset_result = dataset_analysis.get_dataset_analysis_result()
    if not dataset_result:
        dataset_result = build_zero_value_list(5)

    binderhub_result = binderhub_call.get_result()

    result = [repository_url, readme_result[0], readme_result[1], readme_result[2], readme_result[3], readme_result[4],
              readme_result[5], readme_result[6], license_result[0], license_result[1], license_result[2],
              source_code_result[0], source_code_result[1], source_code_result[2], source_code_result[3],
              source_code_result[4], source_code_result[5], source_code_result[6], source_code_result[7],
              source_code_result[8], source_code_result[9], source_code_result[10], source_code_result[11],
              source_code_result[12], source_code_result[13], source_code_result[14], config_analysis[0],
              config_analysis[1], config_analysis[2], config_analysis[3], config_analysis[4], config_analysis[5],
              config_analysis[6], dataset_result[0], dataset_result[1], dataset_result[2], dataset_result[3],
              dataset_result[4], binderhub_result[0]]

    analysis_result.extend(result)

    write_list_to_csv(result, output_file)

    build_terminal_response()


def build_zero_value_list(length):
    zero_value_list = []
    counter = 0
    while counter < length:
        zero_value_list.append(0)
        counter = counter + 1
    return zero_value_list


def create_csv_file(output_file):
    if not os.path.isfile(output_file):
        csv_header = make_csv_header()
        write_list_to_csv(csv_header, output_file)


def make_csv_header():
    return ['repository_url', '# readmes', 'total readme lines', 'average readme lines', '# readme links',
            '# readme paper links', '# not accessible links', '% not accessible links', '# licences',
            '# open-source licenses', '# non-open-source licenses', '# source code files', '# total lines of code',
            '% of code lines', '# total comment lines', '% of comment lines', 'code-comment-ratio',
            'average pylint score', '# jupyter notebooks', '% jupyter notebooks /w header',
            '% jupyter notebooks /w footer', '# random seed declaration lines', '% fixed random seed lines',
            'Model serialization used?', '# hyperparameter logging indicators',
            '% public available libraries in relation to all unique imports in source code (excl. local libs and '
            'python standard libs)',
            '# config files', 'OS specified in config file(s)', '# unique imports in config file(s)',
            '# unique imports in source code file(s)',
            '% strict unique imports in relation to all unique imports in config file(s)',
            '% specified unique (but not strict) imports in relation to all unique imports in config file(s)',
            '% unique imports used in source code + mentioned in config file(s) in relation to all used',
            'dataset folders found?', '# dataset folder candidates', '# dataset file candidates',
            '# found dataset file candidates mentioned in source code',
            '% mentioned dataset files in relation to all found candidate files',
            'out-of-the-box buildable with binderhub']


def check_repository(repository_url, output_file):
    file = open(output_file, "r")
    csv_reader = csv.reader(file)

    lists_from_csv = []
    for row in csv_reader:
        lists_from_csv.append(row)
    for element in lists_from_csv:
        if element[0] == repository_url:
            return 1
    return 0


def write_list_to_csv(result_list, output_file):
    print('\nWrote result to ' + output_file + '\n')
    with open(output_file, 'a', newline='') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(result_list)


def build_terminal_response():
    console = Console()

    print('\n\n')
    print('[bold magenta] ______________________[/bold magenta]')
    print('[bold magenta]|   ANALYSIS RESuLT    |[/bold magenta]')
    print('[bold magenta]|______________________|[/bold magenta]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="right")
    table.add_column("value", justify="left")
    table.add_row('repository url', str(analysis_result[0]))
    table.add_row('# readmes', str(analysis_result[1]))
    table.add_row('total lines', str(analysis_result[2]))
    table.add_row('average lines', str(analysis_result[3]))
    table.add_row('# links', str(analysis_result[4]))
    table.add_row('# paper links', str(analysis_result[5]))
    table.add_row('# not accessible links', str(analysis_result[6]))
    table.add_row('% not accessible links', str(analysis_result[7]))
    table.add_row('# licenses', str(analysis_result[8]))
    table.add_row('# open-source licenses', str(analysis_result[9]))
    table.add_row('# non-open-source licenses', str(analysis_result[10]))
    table.add_row('# source code files', str(analysis_result[11]))
    table.add_row('# total lines of code', str(analysis_result[12]))
    table.add_row('% of code lines', str(analysis_result[13]))
    table.add_row('# total comment lines', str(analysis_result[14]))
    table.add_row('% of comment lines', str(analysis_result[15]))
    table.add_row('code-comment-ratio', str(analysis_result[16]))
    table.add_row('average pylint score (best is 10)', str(analysis_result[17]))
    table.add_row('# jupyter notebooks', str(analysis_result[18]))
    table.add_row('% of jupyter notebooks /w header', str(analysis_result[19]))
    table.add_row('% of jupyter notebooks /w footer', str(analysis_result[20]))
    table.add_row('# random seed lines', str(analysis_result[21]))
    table.add_row('% fixed random seed lines', str(analysis_result[22]))
    table.add_row('Model serializaton used?', str(analysis_result[23]))
    table.add_row('# hyperparameter logging indicators', str(analysis_result[24]))
    table.add_row('% public available libraries in relation to all unique imports in source code (excl. local libs '
                  'and python standard libs)', str(analysis_result[25]))
    table.add_row('# config files', str(analysis_result[26]))
    table.add_row('OS specified in config file(s)', str(analysis_result[27]))
    table.add_row('# unique imports in config file(s)', str(analysis_result[28]))
    table.add_row('# unique imports in source code file(s)', str(analysis_result[29]))
    table.add_row('% strict unique imports in relation to all unique imports in config file(s)',
                  str(analysis_result[30]))
    table.add_row('% specified unique (but not strict) imports in relation to all unique imports in config file(s)',
                  str(analysis_result[31]))
    table.add_row('% unique imports used in source code + mentioned in config file(s) in relation to all used',
                  str(analysis_result[32]))
    table.add_row('dataset folders found?', str(analysis_result[33]))
    table.add_row('# dataset folder candidates', str(analysis_result[34]))
    table.add_row('# dataset file candidates', str(analysis_result[35]))
    table.add_row('# found dataset file candidates mentioned in source code', str(analysis_result[36]))
    table.add_row('% mentioned dataset files in relation to all found candidate files',
                  str(analysis_result[37]))
    table.add_row('out-of-the-box buildable with binderhub?', str(analysis_result[38]))
    console.print(table)
    print('\n')

#!/usr/bin/python3

import filter_repository_artefacts
from os import listdir
from os.path import isfile, join
import re
from rich import print
from rich.console import Console
from rich.table import Table

import source_code_analysis

reg_ext = re.compile("(.+)?((.csv$)|(.png$)|(.jp(e)?g$))")

dataset_folders = []

dataset_file_candidates = []

sc_dataset_analysis = []

dataset_analysis_result = []

# TODO: doc

# Checks if .csv/images are in the possible dataset folders
# We use the retrieved directories from the structure analysis


# folder with 'data' / 'im' + 'g' in name + .csv or .png or .jpg inside -> add files to candidates list
def analyse_datasets():
    dataset_folders.extend(filter_repository_artefacts.get_dataset_folders())
    for candidate in dataset_folders:
        dir_path = candidate[1]

        dir_data = []

        all_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file in all_files:
            if bool(re.match(reg_ext, file)):
                dir_data.append(file)
        if dir_data:
            for data in dir_data:
                dataset_file_candidates.append(data)


def get_dataset_file_candidates():
    return dataset_file_candidates


def get_dataset_analysis_result():
    return dataset_analysis_result


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def build_dataset_response(verbose):
    number_of_dataset_file_candidates = 0
    number_of_dataset_folder_candidates = 0
    number_of_dataset_files_mentioned_sc = 0
    percentage_dataset_files_in_sc = 0

    if not dataset_folders:
        dataset_found = 'No'
        print('found no possible dataset folders')
    else:
        dataset_found = 'Yes'
        number_of_dataset_folder_candidates = len(dataset_folders)
        if not dataset_file_candidates:
            print('found possible dataset folders but no relevant content inside')
        else:
            number_of_dataset_file_candidates = len(dataset_file_candidates)
            sc_dataset_analysis.extend((source_code_analysis.get_mentioned_dataset_files()))
            number_of_dataset_files_mentioned_sc = len(sc_dataset_analysis)
            percentage_dataset_files_in_sc = calculate_percentage(number_of_dataset_files_mentioned_sc,
                                                                  number_of_dataset_file_candidates)

    dataset_analysis_result.extend((dataset_found, number_of_dataset_folder_candidates,
                                    number_of_dataset_file_candidates, number_of_dataset_files_mentioned_sc,
                                    percentage_dataset_files_in_sc))

    console = Console()
    print('\n\n')
    print('[bold] _______________________________________________________[/bold]')
    print('[bold]|[magenta]              DATASET CANDIDATE(s) ANALYSIS            [/magenta]|[/bold]')
    print('[bold]|_______________________________________________________|[/bold]\n')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('dataset folders found?', dataset_found)
    table.add_row('# dataset folder candidates', str(number_of_dataset_folder_candidates))
    table.add_row('# dataset file candidates', str(number_of_dataset_file_candidates))
    table.add_row('# found dataset file candidates mentioned in source code', str(number_of_dataset_files_mentioned_sc))
    table.add_row('% mentioned dataset files in relation to all found candidate files',
                  str(percentage_dataset_files_in_sc))

    console.print(table)
    print('\n')

    if verbose == 1:

        if dataset_folders:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("DATASET FOLDER CANDIDATE(s)", justify="left")
            for folder in dataset_folders:
                table.add_row(folder[1])
            console.print(table)
            print('\n')

        if dataset_file_candidates:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("DATASET FILE CANDIDATE(s)", justify="left")
            for file in dataset_file_candidates:
                table.add_row(file)
            console.print(table)
            print('\n')

        if sc_dataset_analysis:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("DATASET FILE(s) IN SOURCE CODE", justify="left")
            for file in sc_dataset_analysis:
                table.add_row(file)
            console.print(table)
            print('\n')
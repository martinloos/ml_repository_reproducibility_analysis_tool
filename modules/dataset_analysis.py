#!/usr/bin/python3

import modules.filter_repository_artefacts as filter_repository_artefacts
import os
import re
from rich import print
from rich.console import Console
from rich.table import Table

# import modules.source_code_analysis as source_code_analysis

reg_ext = re.compile("(.+)?((.py$)|(.ipynb$)|(.md$))")

dataset_folders = []

dataset_file_candidates = []

sc_dataset_analysis = []

dataset_analysis_result = []

# TODO: doc

# Checks if .csv/images are in the possible dataset folders
# We use the retrieved directories from the structure analysis


# returns a list of files inside directory path incl subdirectories
def get_all_files_in_dir(dir_path):
    list_of_files = os.listdir(dir_path)
    all_files = list()
    for f in list_of_files:
        full_path = os.path.join(dir_path, f)
        if os.path.isdir(full_path):
            all_files = all_files + get_all_files_in_dir(full_path)
        else:
            all_files.append(full_path)

    return all_files


# folder with 'data' / 'im' + 'g' in name + file name not matching regex -> add files to candidates list
# files with data in name + file name not matching regex -> add files to candidates list
def analyse_datasets():
    dataset_folders.extend(filter_repository_artefacts.get_dataset_folders())
    for candidate in dataset_folders:
        dir_path = candidate[1]
        all_files = get_all_files_in_dir(dir_path)
        for file in all_files:
            if '/' in file:
                file_name = file.split('/')[-1]
            else:
                file_name = file

            # adding files inside folder named ?data? or ?im(a)g? excluding ones that match the regex
            if (file_name not in dataset_file_candidates) and (not bool(re.match(reg_ext, file_name))):
                dataset_file_candidates.append(file_name)

    # add files who are named ?data?.? and who do not end with .py etc (see above)
    # get all files with ?data?.? in name from filter repo structure
    # add them to dataset_file_candidates list if not already in it
    files_w_data_in_name = filter_repository_artefacts.get_files_name_data()

    for f in files_w_data_in_name:
        file_name = f[0]
        if (file_name not in dataset_file_candidates) and (not bool(re.match(reg_ext, file_name))):
            dataset_file_candidates.append(file_name)


def get_dataset_file_candidates():
    return dataset_file_candidates


def get_dataset_analysis_result():
    return dataset_analysis_result


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def build_dataset_response(mentioned_dataset_files_in_sc, verbose):
    number_of_dataset_file_candidates = 0
    number_of_dataset_folder_candidates = 0
    number_of_dataset_files_mentioned_sc = 0
    percentage_dataset_files_in_sc = 0

    if (not dataset_folders) and (not dataset_file_candidates):
        dataset_folder_found = 'No'
        print('found no possible datasets')
    else:
        dataset_folder_found = 'Yes'
        number_of_dataset_folder_candidates = len(dataset_folders)
        if not dataset_file_candidates:
            print('Found possible dataset folders but no relevant content inside')
        else:
            number_of_dataset_file_candidates = len(dataset_file_candidates)
            sc_dataset_analysis.extend(mentioned_dataset_files_in_sc)
            number_of_dataset_files_mentioned_sc = len(sc_dataset_analysis)
            percentage_dataset_files_in_sc = calculate_percentage(number_of_dataset_files_mentioned_sc,
                                                                  number_of_dataset_file_candidates)

    dataset_analysis_result.extend((dataset_folder_found, number_of_dataset_folder_candidates,
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
    table.add_row('dataset folders found?', dataset_folder_found)
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
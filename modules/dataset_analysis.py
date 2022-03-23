#!/usr/bin/python3

import modules.filter_repository_artifacts as filter_repository_artifacts
import os
import re
from rich import print
from rich.console import Console
from rich.table import Table

# File extension regex used to eliminate .py, .ipynb and .md files which are for sure no dataset files
reg_ext = re.compile("(.+)?((.py$)|(.ipynb$)|(.md$))")
# Stores all the found dataset folders from the filter_repository_artifacts module.
dataset_folders = []
# Stores all the found dataset file candidates. These are all files with 'data' in name and files inside the found
# dataset folders which do not match reg_ext.
dataset_file_candidates = []
# Stores the result of the source code analysis. Dataset files in this list are mentioned in at least one code file.
sc_dataset_analysis = []
# Stores the overall dataset analysis result.
dataset_analysis_result = []


# returns a list of files inside the provided directory path including subdirectories
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
    """
        Firstly, for all the found dataset folders the containing files are stored. For each found file: If the name of
        it does not match the reg_ext, which excludes .py, .ipynb and .md files because they are for sure not datasets,
        the file will be stored in the dataset_file_candidates list. Also, all files in the repository with 'data' in
        the name will be stored there too. This list will be used by the source_code_analysis module in order to check
        which of these candidates are actually mentioned in the source code. For these matches we then assume that they
        are actual datasets.
    """
    dataset_folders.extend(filter_repository_artifacts.get_dataset_folders())
    for candidate in dataset_folders:
        dir_path = candidate[1]
        all_files = get_all_files_in_dir(dir_path)
        for file in all_files:
            if '/' in file:
                file_name = file.split('/')[-1]
            else:
                file_name = file

            # adding files inside the found dataset folder(s) excluding ones that match the regex
            if (file_name not in dataset_file_candidates) and (not bool(re.match(reg_ext, file_name))):
                dataset_file_candidates.append(file_name)

    files_w_data_in_name = filter_repository_artifacts.get_files_name_data()

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
    """
        Builds the overall dataset analysis result using the stored information, and the found mentions of dataset file
        candidates in the source code (mentioned_dataset_files_in_sc). Prints the result out in the command line and
        stores it in the dataset_analysis_result. If verbose is specified, prints out additional information.

        Parameters:
            mentioned_dataset_files_in_sc (List[str]): A list of all the found dataset file candidates who are
            mentioned in the source code.
            verbose (int): Default = 0 if verbose (additional command line information) off.
    """
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

    # if verbose specified in terminal command prints out additional information
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

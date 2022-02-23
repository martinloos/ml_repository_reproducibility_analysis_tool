#!/usr/bin/python3

# TODO: doc

import logging
import pathlib
import repository_structure
from rich import print
from rich.console import Console
from rich.table import Table
import re

logger = logging.getLogger('log')

reg = re.compile("(((.+)?data(.+)?)|((.+)?im(a)?g))")
dataset_folders = []
files_name_data = []
dvc_folder = []
dvc_files = []

accepted_files = {'readme', 'requirements', 'config.yml', 'config.yaml', 'conda.env', 'license', 'dockerfile'}
readme = []
source_code_files = []
config_files = []
repo_license = []

config_file_reg = \
    re.compile("(((.+)?(conda|env)(.+)?\\.y(a)?ml)|((.+)?requirements(.+)?\\.txt)|((.+)?(^|[^.])(docker)(.+)?))")


def get_repository_structure(local_repo_dir_path):
    structure_response = repository_structure.get_structure(local_repo_dir_path)
    return structure_response


def get_relevant_artefacts(local_repo_dir_path, verbose):
    structure_response = get_repository_structure(local_repo_dir_path)
    directories = structure_response[0]
    files = structure_response[1]

    for d in directories:
        if bool(re.match(reg, d[0].lower())):
            dataset_folders.append(d)
        if d[0].lower() == '.dvc':
            dvc_folder.append(d)

    for f in files:
        file_name = f[0].lower()
        file_extension = pathlib.PurePosixPath(file_name).suffix
        if file_extension == '.ipynb':
            source_code_files.append(f)
        elif file_extension == '.py':
            source_code_files.append(f)
        elif file_extension == '.dvc':
            dvc_files.append(f)
        elif 'readme' in file_name:
            readme.append(f)
        elif 'license' in file_name:
            # for .doctree: UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0: invalid
            # start byte
            if '.doctree' not in file_name:
                repo_license.append(f)
        elif 'data' in file_name:
            files_name_data.append(f)
        elif '.dockerignore' not in file_name:
            if bool(re.match(config_file_reg, file_name)):
                config_files.append(f)

    if verbose == 1:
        print('\n')
        print('[bold magenta] _________________________________________________[/bold magenta]')
        print('[bold magenta]|     RESULT OF REPOSITORY STRUCTURE ANALYSIS     |[/bold magenta]')
        print('[bold magenta]|_________________________________________________|[/bold magenta]\n')

        console = Console()

        if not dataset_folders:
            logger.warning('No dataset folder(s) detected.')
            print(':pile_of_poo: [bold red]No dataset folder(s) detected.[/bold red]')
        else:
            print('[bold green] DATASET FOLDER(s)[/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("Folder name", justify="left")
            table.add_column("Folder path", justify="left")
            for folder in dataset_folders:
                table.add_row(folder[0], folder[1])
            console.print(table)
            print('\n')

        if not readme:
            logger.warning('No readme(s) detected.')
            print(':pile_of_poo: [bold red]No readme(s) detected.[/bold red]')
        else:
            print('[bold green] README(s)[/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for r in readme:
                table.add_row(r[0], r[1])
            console.print(table)
            print('\n')

        if not config_files:
            logger.warning('No config file(s) detected.')
            print(':pile_of_poo: [bold red]No config file(s) detected.[/bold red]')
        else:
            print('[bold green] CONFIG FILE(s)[/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for file in config_files:
                table.add_row(file[0], file[1])
            console.print(table)
            print('\n')

        if not repo_license:
            logger.warning('No license(s) detected.')
            print(':pile_of_poo: [bold red]No license(s) detected.[/bold red]')
        else:
            print('[bold green] LICENSE FILE(s)[/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for lic in repo_license:
                table.add_row(lic[0], lic[1])
            console.print(table)
            print('\n')

        if not source_code_files:
            logger.warning('No jupyter notebook(s) or .py files detected.')
            print(':pile_of_poo: [bold red]No jupyter notebook(s) or .py files detected.[/bold red]')
        else:
            print('[bold green] JUPYTER NOTEBOOK(s) + PYTHON FILES [/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for jn in source_code_files:
                table.add_row(jn[0], jn[1])
            console.print(table)
            print('\n')


def get_readme():
    return readme


def get_license():
    return repo_license


def get_dataset_folders():
    return dataset_folders


def get_files_name_data():
    return files_name_data


def get_config_files():
    return config_files


def get_source_code_files():
    return source_code_files


def get_dvc_folder():
    return dvc_folder


def get_dvc_files():
    return dvc_files

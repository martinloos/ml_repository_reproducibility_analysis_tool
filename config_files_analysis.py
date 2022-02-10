#!/usr/bin/python3

import re

import filter_repository_artefacts
import source_code_analysis
from rich import print
from rich.console import Console
from rich.table import Table

# TODO: doc

config_analysis_result = []

config_files = []
all_unique_lib_imports = []
strict_lib_imports = []
specified_not_strict_imports = []
list_of_specified_os = []

source_code_imports = []

used_but_not_in_config = []
used_and_in_config = []

# Checks if used libraries in the source code are specified
# Checks if versions are specified
# Checks if libraries are public


def analyse_config_files(verbose):
    sc_imports = source_code_analysis.get_imports()
    source_code_imports.extend(sc_imports)
    retrieve_all_config_imports()

    compare_config_imp_with_sc_imp()

    build_config_analysis_result(verbose)


# 1 collect all imports from config files
def retrieve_all_config_imports():
    config_files.extend((filter_repository_artefacts.get_config_files()))

    for file in config_files:
        file_name = file[0].lower()
        print('config file name: ')
        print(file_name)
        file_path = file[1]

        config_lines = []
        error = 0

        # e.g. https://github.com/KristiyanVachev/Leaf-Question-Generation will throw UnicodeDecodeError
        # but works with other solution whereas https://github.com/dmitrijsk/AttentionHTR works with the first
        # solution better (most repos work with the first one already, so the other is just a backup solution)
        try:
            config_text = open(file_path, "r")
            config_read = config_text.readlines()
            config_text.close()
            for line in config_read:
                config_lines.append(line.lower().replace('\n', ''))
        except UnicodeDecodeError:
            error = 1

        if error == 1:
            with open(file_path, "rb") as config_text:
                conf_text_lines = config_text.read()
                print('config file line: ')
                print(conf_text_lines)
                # thanks to https://stackoverflow.com/questions/67734203/reading-a-txt-and-getting-weird-behavior
                dec_lines = conf_text_lines.decode('utf-16le', 'ignore')
                dec_llist = dec_lines.split('\n')
                for line in dec_llist:
                    config_lines.append(line.lower())

        # requirements
        if 'requirements' in file_name:
            retrieve_imports_from_requirements(config_lines)

        # 'WILDCARD + conda OR env + WILDCARD +..y + optional a + ml'
        reg = re.compile("(.+)?(conda|env)(.+)?.y(a)?ml")

        if bool(re.match(reg, file_name)):
            retrieve_imports_from_env_yml(config_lines)

        # docker
        docker_reg = re.compile("dockerfile")

        if bool(re.fullmatch(docker_reg, file_name)):
            retrieve_imports_from_dockerfile(config_lines)


# developed against: https://github.com/iterative/example-get-started/blob/master/src/requirements.txt
# and: https://github.com/tirthajyoti/Machine-Learning-with-Python/blob/master/Deployment
# /Linear_regression/requirements.txt
def retrieve_imports_from_requirements(config_lines):
    for line in config_lines:
        line = line.replace('\n', '').replace(' ', '').replace('\\', '')
        if not (line.startswith('#') or line.startswith('-')):

            # rename import if needed
            line = replace_config_imp_name(line)

            # strict or specified imports?
            if '=' in line:
                line = parse_specified_line(line)

            if line not in all_unique_lib_imports:
                all_unique_lib_imports.append(line)


def parse_specified_line(config_line):
    line = extract_lib_name_from_requirements(config_line)
    # strict import?
    reg = re.compile("(.+)?(~|!|<|>)")
    # not strict but specified import?
    # check for unstrict imports ~, !, <, > and remove the character from line if found
    if bool(re.match(reg, config_line)):
        if line not in specified_not_strict_imports:
            specified_not_strict_imports.append(line)
    # else = or ==
    else:
        if line not in strict_lib_imports:
            strict_lib_imports.append(line)

    return line


# developed against: https://github.com/mlflow/mlflow/blob/master/examples/sklearn_elasticnet_diabetes/linux/conda.yaml
def retrieve_imports_from_env_yml(config_lines):
    # everything after dependencies: and before next line with no whitespace at the first char
    # if line starts with - and not ends with : replace - with '' and remove whitespace
    # probably same with conda env
    dependencies = 0
    indent_helper = 0

    for line in config_lines:
        line = line.replace('\n', '').replace('\\', '')

        if line.startswith('dependencies:'):
            dependencies = 1
        # first char of line is not whitespace but also not dependencies:
        elif not line.startswith(' '):
            dependencies = 0
            indent_helper = 0
        # lines that start with a whitespace (indent) + in dependencies section
        elif dependencies == 1:
            line_indent = len(line.split('-')[0])
            # not import declaration (maybe something like - pip:)
            if '-' in line and line.endswith(':'):
                indent_helper = len(line.split('-')[0])
            # uncorrect indent (everything inside e.g. - pip: ....)
            elif '-' in line and 0 < indent_helper <= line_indent:
                indent_helper = line_indent
            # everything inside dependencies but not matching the above -> must be libraries + python versions etc.
            else:
                indent_helper = 0
                line = line.replace('-', '').replace(' ', '')

                # strict or specified imports?
                if '=' in line:
                    line = parse_specified_line(line)

                if line not in all_unique_lib_imports:
                    all_unique_lib_imports.append(line)


# developed against: https://github.com/kubeflow/examples
# TODO: improve precision (not all found cases covered)
def retrieve_imports_from_dockerfile(config_lines):

    pip_install_section = 0

    imp_list = []

    for line in config_lines:
        lower_line = line.lower()
        if lower_line.startswith('from'):
            spec_os = line.split()[1]
            list_of_specified_os.append(spec_os)
        elif '&&' in lower_line:
            pip_install_section = 0
        elif lower_line.startswith('run pip'):
            if len(lower_line.split()) == 4:
                imp = line.split()[3].replace('\\', '')
                imp_list.append(imp)
            pip_install_section = 1
        elif lower_line.startswith(' ') and pip_install_section == 1:
            imp = line.replace('\ ', '').split()[-1].replace('\\', '')
            imp_list.append(imp)
        else:
            pip_install_section = 0

    for imp in imp_list:
        if imp:
            # strict or specified imports?
            if '=' in imp:
                imp = parse_specified_line(imp)

            if imp not in all_unique_lib_imports:
                all_unique_lib_imports.append(imp)

    # OS? FROM ubuntu:16.04 -> if os specified -> which version + which file
    # RUN pip .... \ till && everything between -> remove all \ and whitespace


def replace_config_imp_name(imp_line):
    if 'scikit-learn' in imp_line:
        imp_line = imp_line.replace('scikit-learn', 'sklearn')
    elif 'pyaml' in imp_line:
        imp_line = imp_line.replace('pyaml', 'yaml')

    return imp_line


def extract_lib_name_from_requirements(imp_line):
    imp_lib = imp_line.split('=')[0].replace('=', '')

    reg = re.compile("(.+)?(~|!|<|>)")
    # check for unstrict imports ~, !, <, > and remove the character from line if found
    if bool(re.match(reg, imp_lib)):
        imp_lib = imp_lib[:-1]

    return imp_lib


# 3 check how many of the used libraries are specified in the configs
def compare_config_imp_with_sc_imp():
    for imp in source_code_imports:
        imp_tmp = imp.lower()
        if imp_tmp not in all_unique_lib_imports:
            if imp_tmp not in used_but_not_in_config:
                used_but_not_in_config.append(imp)
        elif imp_tmp not in used_and_in_config:
            used_and_in_config.append(imp)

# 4 check if imports are all public available
# TODO: Ideas on how to do that


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def get_config_analysis_result():
    return config_analysis_result


# TODO: % publicly available libraries of all used
def build_config_analysis_result(verbose):
    number_of_config_files = len(config_files)

    if len(list_of_specified_os) > 0:
        os_specified = 'Yes'
    else:
        os_specified = 'No'

    number_of_unique_config_imports = len(all_unique_lib_imports)

    number_of_unique_used_imports = len(source_code_imports)
    # how many of all mentioned imports in config files are strictly defined
    percentage_strict_imports = 0
    # how many of all mentioned imports in config files are specified but not strictly
    percentage_not_strict_but_specified_imports = 0
    if number_of_unique_config_imports > 0:
        percentage_strict_imports = calculate_percentage(len(strict_lib_imports), number_of_unique_config_imports)
        percentage_not_strict_but_specified_imports = calculate_percentage(len(specified_not_strict_imports),
                                                                           number_of_unique_config_imports)

    # how many of the used imports in source code were mentioned in config files
    percentage_of_used_imports = 0
    if number_of_unique_used_imports > 0:
        percentage_of_used_imports = calculate_percentage(len(used_and_in_config), number_of_unique_used_imports)

    config_analysis_result.extend((number_of_config_files, os_specified, number_of_unique_config_imports,
                                   number_of_unique_used_imports, percentage_strict_imports,
                                   percentage_not_strict_but_specified_imports, percentage_of_used_imports))

    console = Console()

    print('\n\n')
    print('[bold] _______________________________________________________[/bold]')
    print('[bold]|[magenta]                  CONFIG FILE(s) ANALYSIS              [/magenta]|[/bold]')
    print('[bold]|_______________________________________________________|[/bold]\n')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# config files', str(number_of_config_files))
    table.add_row('OS specified in config file(s)', os_specified)
    table.add_row('# unique imports in config file(s)', str(number_of_unique_config_imports))
    table.add_row('# unique imports in source code file(s)', str(number_of_unique_used_imports))
    table.add_row('% strict unique imports in relation to all unique imports in config file(s)',
                  str(percentage_strict_imports))
    table.add_row('% specified unique (but not strict) imports in relation to all unique imports in config file(s)',
                  str(percentage_not_strict_but_specified_imports))
    table.add_row('% unique imports used in source code + mentioned in config file(s) in relation to all used',
                  str(percentage_of_used_imports))

    console.print(table)
    print('\n')

    if verbose == 1:

        if all_unique_lib_imports:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE LIBRARIES IN CONFIG FILE(s)", justify="left")
            for lib in all_unique_lib_imports:
                table.add_row(lib)
            console.print(table)
            print('\n')

        if strict_lib_imports:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE STRICT LIBRARIES IN CONFIG FILE(s)", justify="left")
            for lib in strict_lib_imports:
                table.add_row(lib)
            console.print(table)
            print('\n')

        # strict specified would be library == version, not strict e.g. library >= version
        if specified_not_strict_imports:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE SPECIFIED (BUT NOT STRICT) LIBRARIES IN CONFIG FILE(s)", justify="left")
            for lib in specified_not_strict_imports:
                table.add_row(lib)
            console.print(table)
            print('\n')

        if source_code_imports:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE USED LIBRARIES IN SOURCE CODE FILE(s)", justify="left")
            for lib in source_code_imports:
                table.add_row(lib)
            console.print(table)
            print('\n')

        if used_and_in_config:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE USED LIBRARIES WHO ARE ALSO MENTIONED IN CONFIG FILE(s)", justify="left")
            for lib in used_and_in_config:
                table.add_row(lib)
            console.print(table)
            print('\n')

        if used_but_not_in_config:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("UNIQUE USED LIBRARIES WHO ARE NOT MENTIONED IN CONFIG FILE(s)", justify="left")
            for lib in used_but_not_in_config:
                table.add_row(lib)
            console.print(table)
            print('\n')



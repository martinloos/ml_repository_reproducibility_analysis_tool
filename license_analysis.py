#!/usr/bin/python3

import filter_repository_artefacts
from rich import print
from rich.console import Console
from rich.table import Table

# TODO: doc

# assuming license to be open source if they are according to FSF
# see: https://en.wikipedia.org/wiki/Comparison_of_free_and_open-source_software_licences
fsf_open_source_licenses = ['Academic Free', 'Affero General Public', 'Apache',
                            'Apple Public Source License 2.0', 'Aristic License 2.0', 'BSD',
                            'Boost Software', 'CeCILL', 'Common Development and Distribution',
                            'Common Public', 'Creative Commons', 'Cryptix General',
                            'Eclipse Public', 'Educational Community', 'Eiffel Forum',
                            'European Union Public', 'GNU', 'IBM Public',
                            'Intel Open Source', 'ISC', 'LaTeX Project Public',
                            'Microsoft Public', 'Microsoft Reciprocal', 'MIT',
                            'Mozilla Public', 'Netscape Public', 'Open Software',
                            'OpenSSL', 'PHP License', 'Python Software Foundation',
                            'Q Public License', 'Sleepycat License',
                            'Sun Industry Standards Source', 'Sun Public',
                            'Unilicense', 'W3C Software Notice', 'WTFPL',
                            'Do What The Fuck You Want', 'XFree86 1.1',
                            'zlib/libpng', 'Zope Public']

open_source_licenses = []
non_open_source_licenses = []

license_result = []


def analyse_license(verbose):
    repo_license = filter_repository_artefacts.get_license()
    if repo_license:
        for file in repo_license:
            license_name = file[0]
            local_license_path = file[1]
            license_text = get_license_text(local_license_path)
            detected_license = detect_license_type(license_text)
            if not detected_license:
                non_open_source_license = license_name, local_license_path
                non_open_source_licenses.append(non_open_source_license)
            else:
                open_source_license = license_name, local_license_path
                open_source_licenses.append(open_source_license)
    build_license_response(verbose)


def get_license_text(license_path):
    license_file = open(license_path, "r")
    license_text = license_file.read()
    license_file.close()

    return license_text


def detect_license_type(license_text):
    detected_license = []
    for license_type in fsf_open_source_licenses:
        if license_type in license_text:
            detected_license.append(license_type)
    return detected_license


def get_license_result():
    return license_result


def build_license_response(verbose):
    number_of_open_source_licenses = len(open_source_licenses)
    number_of_non_open_source_licenses = len(non_open_source_licenses)
    total_number_of_licenses = number_of_open_source_licenses + number_of_non_open_source_licenses

    license_result.append(total_number_of_licenses)
    license_result.append(number_of_open_source_licenses)
    license_result.append(number_of_non_open_source_licenses)

    console = Console()

    print('\n')
    print('[bold magenta] ____________________________________[/bold magenta]')
    print('[bold magenta]|     RESULT OF LICENSE ANALYSIS     |[/bold magenta]')
    print('[bold magenta]|____________________________________|[/bold magenta]\n')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# licenses', str(total_number_of_licenses))
    table.add_row('# open-source licenses', str(number_of_open_source_licenses))
    table.add_row('# non-open-source licenses', str(number_of_non_open_source_licenses))
    console.print(table)
    print('\n')

    if verbose == 1:
        print('\n\n')
        print('[bold] ____________________________________________________[/bold]')
        print('[bold]|      LICENSE ANALYSIS: [magenta]ADDITIONAL INFORMATION[/magenta]      |[/bold]')
        print('[bold]|____________________________________________________|[/bold]\n')
        if open_source_licenses:
            print('[bold green] OPEN-SOURCE LICENSES[/bold green]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for element in open_source_licenses:
                table.add_row(element[0], element[1])
            console.print(table)
            print('\n')

        if non_open_source_licenses:
            print('[bold red] NON-OPEN-SOURCE LICENSES[/bold red]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("File name", justify="left")
            table.add_column("File path", justify="left")
            for element in non_open_source_licenses:
                table.add_row(element[0], element[1])
            console.print(table)
            print('\n')

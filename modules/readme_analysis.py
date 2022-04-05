#!/usr/bin/python3

import logging
import requests
import modules.filter_repository_artifacts as filter_repository_artifacts
import re
from rich import print
from rich.console import Console
from rich.table import Table
from charset_normalizer import detect

# regex for detecting all kinds of links in text
# tested: line break would influence regex, so keep it in one line
regex = r'(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\\\'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))'

logger = logging.getLogger('log')
# checking links in each readme if they contain one of these keywords
# (if yes, we assume they link to a paper publication)
list_of_paper_url_keywords = ['doi', 'arxiv', 'jmlr', 'ieeexplore',
                              'springer', 'igi-global', 'citeseerx',
                              'morganclaypool', 'openaccess', 'proceedings',
                              'dl.acm', 'researchgate', 'aaai.org',
                              'annualreviews']
# if the detected possible paper url ends with one of these types it's not a paper link
# e.g. maybe it's a png referenced from one of the sites above
file_types = {'.txt', '.jpeg', '.jpg', '.png', '.gif'}
# checking if a binder badge is included in a readme file
binder_badge_keyword = '![Binder]'
# Stores the name, file_path, length and whether it includes a binder badge for each readme file
readme_data = []
# Stores all the found links in the readme file(s)
readme_links = []
# Stores all the found paper links in the readme file(s)
readme_paper_links = []
# Stores all links which are not accessible
inaccessible_readme_links = []
# Stores the overall result of the readme file(s) analysis
readme_analysis = []


def analyse_readme(verbose):
    """
        Firstly, all the found readme file(s) are collected from the filter_repository_artifacts module. For each
        readme file the following properties are analyzed: Length, links, the inclusion of a binder badge, and checks
        if a 'data' section, or a reference to a known dataset (see assets/dataset_names.txt) is in at least one of the
        readmes. All the links will be checked whether they are accessible or not. Also, if they are paper links.
        Lastly, the overall result is built, and the result is printed out in the command line. If verbose is
        specified, additional information is printed out.

        Parameters:
            verbose (int): Default = 0 if verbose (additional command line information) off.
    """
    readme = filter_repository_artifacts.get_readme()
    counter = 1
    if readme:
        for file in readme:
            readme_name = file[0]
            readme_file_path = file[1]
            logger.info('Processing readme ' + str(counter) + ' out of ' + str(len(readme)) + ' (' + readme_name + ')')
            encoding = get_encoding(readme_file_path)
            readme_text = parse_readme_text(readme_file_path, encoding)
            readme_text_lst = parse_readme_lst(readme_file_path, encoding)
            # from here analysis method calls
            length = readme_length(readme_file_path, encoding)
            links = get_readme_links(readme_text)
            test_readme_links(links, readme_file_path)
            has_binder_badge = check_binder_badge(readme_text)
            has_dataset_mentioned = check_data_section_text(readme_text_lst)
            readme_files = [readme_name, readme_file_path, length, has_binder_badge, has_dataset_mentioned]
            readme_data.append(readme_files)
            counter = counter + 1
        build_readme_response(verbose)
    else:
        logger.warning('Found no readme to analyse')


def get_encoding(readme_path):
    with open(readme_path, 'rb') as f:
        data = f.read()  # or a chunk, f.read(1000000)
    encoding = detect(data).get("encoding")

    return encoding


def parse_readme_text(readme_path, encoding_type):
    readme_file = open(readme_path, "r", encoding=encoding_type)
    readme_text = readme_file.read()
    readme_file.close()

    return readme_text


def parse_readme_lst(readme_path, encoding_type):
    readme_file = open(readme_path, "r", encoding=encoding_type)
    readme_text = readme_file.readlines()
    readme_file.close()

    return readme_text


def readme_length(readme_path, encoding_type):
    i = 0
    with open(readme_path, encoding=encoding_type) as r:
        for i, l in enumerate(r):
            pass
    return i + 1


def get_readme_links(readme_text):
    return re.findall(regex, readme_text)


def check_binder_badge(readme_text):
    is_present = 0
    if binder_badge_keyword in readme_text:
        is_present = 1
    return is_present


def test_readme_links(links, file_path):
    for link in links:
        readme_links.append(link)
        try:
            # test if link starts with http or https
            if not re.match('(?:http|https)://', link):
                link = 'https://' + link
            lower_case_link = link.lower()
            check_if_link_from_paper_publisher(lower_case_link)
            if '.zip' not in link:
                r = requests.get(link)
                if str(r.status_code) == '404':
                    inaccessible_readme_link = link, file_path
                    inaccessible_readme_links.append(inaccessible_readme_link)
        except requests.ConnectionError as exception:
            inaccessible_readme_link = link, file_path
            inaccessible_readme_links.append(inaccessible_readme_link)


def check_if_link_from_paper_publisher(link):
    for publisher in list_of_paper_url_keywords:
        if publisher in link:
            is_unwanted_file = 0
            for f_type in file_types:
                if f_type in link:
                    is_unwanted_file = 1
            if is_unwanted_file == 0:
                readme_paper_links.append(link)


def parse_known_datasets():
    # loading names of known datasets into list
    dataset_names_file = open('assets/dataset_names.txt', "r", encoding='utf-8')
    datasets_text_tmp = dataset_names_file.readlines()
    dataset_names_file.close()

    dataset_text = []

    for line in datasets_text_tmp:
        dataset_text.append(line.lower().replace('\n', ''))

    return dataset_text


def check_for_data_section(readme_text):
    # stores content of 'data' sections in the readme file in list
    reg = "(.*?data.*?|.*?dataset.*?)"
    data_set_section = 0
    data_set_section_text = []

    for line in readme_text:
        line_tmp = line.lower().strip()
        if (line_tmp.startswith('#')) and (bool(re.match(reg, line_tmp))):
            data_set_section = 1
        elif line_tmp.startswith('#'):
            data_set_section = 0
        elif data_set_section == 1:
            data_set_section_text.append(line_tmp)

    return data_set_section_text


def check_data_section_text(readme_text):
    # checks if either at least one link is found in a "data (set)" section of the readme
    # or if we find a known dataset reference in the readme text
    found_mentioned_ds = 0
    data_section_text_lst = check_for_data_section(readme_text)

    data_section_string = ''.join(map(str, data_section_text_lst))

    if data_section_string:
        data_section_links = re.findall(regex, data_section_string)

        if data_section_links:
            found_mentioned_ds = 1

    # no links in data section found, we then check if one of the datasets from assets/dataset_names.txt mentioned
    if found_mentioned_ds == 0:
        # parse dataset names from txt file
        popular_dataset_lst = parse_known_datasets()
        readme_text_string = ''.join(map(str, readme_text))

        for popular_dataset in popular_dataset_lst:
            if (found_mentioned_ds == 0) and (popular_dataset in readme_text_string):
                found_mentioned_ds = 1

    if found_mentioned_ds == 1:
        return 1

    return 0


def get_readme_analysis():
    return readme_analysis


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def build_readme_response(verbose):
    number_of_readmes = len(readme_data)
    readme_length_sum = 0
    readme_with_binder_badge = []
    percentage_of_inaccessible_links = 0
    found_dataset_reference = 0

    for element in readme_data:
        readme_length_sum = readme_length_sum + element[2]
        is_binder_badge_present = element[3]
        if is_binder_badge_present == 1:
            readme_with_binder_badge.append(element[1])
        if element[4] == 1:
            found_dataset_reference = 1

    average_readme_length = round(readme_length_sum / number_of_readmes, 2)
    total_number_of_links = len(readme_links)
    total_number_of_paper_links = len(readme_paper_links)
    total_number_of_inaccessible_links = len(inaccessible_readme_links)
    if not total_number_of_links == 0:
        percentage_of_inaccessible_links = calculate_percentage(total_number_of_inaccessible_links,
                                                                total_number_of_links)

    readme_analysis.append(number_of_readmes)
    readme_analysis.append(readme_length_sum)
    readme_analysis.append(average_readme_length)
    readme_analysis.append(total_number_of_links)
    readme_analysis.append(total_number_of_paper_links)
    readme_analysis.append(total_number_of_inaccessible_links)
    readme_analysis.append(percentage_of_inaccessible_links)
    readme_analysis.append(found_dataset_reference)

    console = Console()

    print('\n')
    print('[bold magenta] ________________________________[/bold magenta]')
    print('[bold magenta]|   RESULT OF README ANALYSIS    |[/bold magenta]')
    print('[bold magenta]|________________________________|[/bold magenta]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# readmes', str(number_of_readmes))
    table.add_row('total lines', str(readme_length_sum))
    table.add_row('average lines', str(average_readme_length))
    table.add_row('# links', str(total_number_of_links))
    table.add_row('# paper links', str(total_number_of_paper_links))
    table.add_row('# not accessible links', str(total_number_of_inaccessible_links))
    table.add_row('% not accessible links', str(percentage_of_inaccessible_links))
    if found_dataset_reference == 1:
        table.add_row('Dataset section with reference', 'Yes')
    else:
        table.add_row('Dataset section with reference', 'No')
    console.print(table)
    print('\n')

    # if verbose specified in terminal command prints out additional information
    if verbose == 1:
        print('\n\n')
        print('[bold] ____________________________________________________________[/bold]')
        print('[bold]|          README ANALYSIS: [magenta]ADDITIONAL INFORMATION[/magenta]           |[/bold]')
        print('[bold]|____________________________________________________________|[/bold]\n')

        if readme_links:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("README: LIST OF LINKS", justify="left")
            for link in readme_links:
                table.add_row(link)
            console.print(table)
            print('\n')

        if readme_paper_links:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("README: LIST OF PAPER LINKS", justify="left")
            for link in readme_paper_links:
                table.add_row(link)
            console.print(table)
            print('\n')

        if inaccessible_readme_links:
            print('[bold red] README: LIST OF NOT ACCESSIBLE LINKS[/bold red]')
            table = Table(show_header=True, header_style="bold dim")
            table.add_column("Link", justify="left")
            table.add_column("File path", justify="left")
            for link in inaccessible_readme_links:
                table.add_row(link[0], link[1])
            console.print(table)
            print('\n')

        if readme_with_binder_badge:
            table = Table(show_header=True, header_style="bold yellow")
            table.add_column("README: READMES CONTAINING A BINDER BADGE", justify="left")
            for element in readme_with_binder_badge:
                table.add_row(element)
            console.print(table)
            print('\n')

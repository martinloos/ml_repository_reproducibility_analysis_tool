#!/usr/bin/python3

import csv
import os

import readme_analysis
import license_analysis


# TODO: doc
# TODO: implement
# Builds result with retrieved data
# Stores result in file

analysis_result = []


def build_result(repository_url, output_file):

    readme_result = readme_analysis.get_readme_analysis()
    if not readme_result:
        readme_result = build_zero_value_list(7)

    license_result = license_analysis.get_license_result()
    if not license_result:
        license_result = build_zero_value_list(3)
    result = [repository_url, readme_result[0], readme_result[1], readme_result[2], readme_result[3], readme_result[4],
              readme_result[5], readme_result[6], license_result[0], license_result[1], license_result[2]]

    analysis_result.append(result)

    write_list_to_csv(result, output_file)


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
            '# open-source licenses', '# non-open-source licenses']


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
    with open(output_file, 'a', newline='') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(result_list)

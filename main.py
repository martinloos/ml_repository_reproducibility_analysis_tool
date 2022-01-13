#!/usr/bin/python3

# main.py is the entrance point for the machine learning reproducibility analyzer

# TODO: README how to set up + use this tool (why useful + options to run)
# TODO: maybe provide logs also in a persistent log file (additional)
# TODO: MAKE CLEAN UP optional? -> Maybe someone wants to keep the repo locally

import getopt
import logging
import sys
import shutil
import re
from rich import print

import repository_cloner
import filter_repository_artefacts
import readme_analysis
import license_analysis
import source_code_analysis
import config_files_analysis
import dataset_analysis
import result_builder


# TODO: give user possibility to specify BinderHub himself
# TODO: give user possibility to specify it himself
csv_path = '/tmp/'
csv_name = 'ml_repo_reproducibility_analyzer'


def main(argv):
    logger = logging.getLogger('log')
    syslog = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    syslog.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(syslog)

    banner_text = open("banner.txt")

    lines = banner_text.readlines()
    for line in lines:
        print(line)

    verbose = 0
    try:
        opts, args = getopt.getopt(argv, "hvu:", ["help", "url=", "verbose"])
        if not opts:
            logger.error('No command specified: Use "python3 main.py -h" for help.')
            sys.exit()
    except getopt.GetoptError:
        logger.error('Use "python3 main.py -h" for help.')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):

            print(' _____________________________________________________________________')
            print('|                                                                     |')
            print('|                      [bold]HELPFUL INFORMATION[/bold]                            |')
            print('|_____________________________________________________________________|')
            print('|                                                                     |')
            print('|  [bold magenta]usage:           main.py -u <GitHub Repository URL>[/bold magenta]                '
                  '|')
            print('|                                                                     |')
            print('|  argument:                                                          |')
            print('|  -u, --url        URL of the GitHub Repository.                     |')
            print('|                                                                     |')
            print('|  optional:                                                          |')
            print('|  -v, --verbose    Additional information provided.                  |')
            print('|  -h, --help       Prints out helpful information.                   |')
            print('|_____________________________________________________________________|')
            sys.exit()
        if opt in ('-v', '--verbose'):
            verbose = 1
    for opt, arg in opts:
        if opt in ('-u', '--url'):
            repository_url = str(arg.strip())

            if not repository_url:
                logger.error('No URL provided. Use "python3 main.py -h" for help.')
                sys.exit()

            # formats repo link correctly in order to ensure the use of https
            if not re.match('(?:https)://', repository_url):
                if not re.match('(?:http)://', repository_url):
                    repository_url = 'https://' + repository_url
                # replace http with https
                elif 'http' in repository_url:
                    repository_url = repository_url.replace('http', 'https')

            # assuming that the repository is stored on github or gitlab
            if 'github' not in repository_url:
                logger.error('URL incorrect. Accepted are repositories from github. Use "python3 main.py -h" for help.')
                sys.exit()

            # create output_file if not already there
            # checks if repository already analyzed in output file
            output_file = csv_path + csv_name + '.csv'
            result_builder.create_csv_file(output_file)
            if result_builder.check_repository(repository_url, output_file):
                logger.info('Repository ' + repository_url + ' already in result ' + output_file)
                print("\n:smiley: [bold green]Repository already analyzed.[/bold green]\n")
                sys.exit()

            # downloads public repository
            logger.info('Downloading repository ' + repository_url + ' ...')
            local_repo_dir = repository_cloner.clone_repo(repository_url)
            logger.info('Finished downloading ' + repository_url)

            # analysis of the repository structure
            # retrieve relevant artefacts (readmes, licenses, dataset/images folders, jupyter notebooks, config files)
            print("\n:smiley: [bold green]Started repository analysis ...[/bold green]\n")
            filter_repository_artefacts.get_relevant_artefacts(local_repo_dir, verbose)
            logger.info('Finished detecting relevant repository artefacts.')

            # checks the readmes found for specified attributes
            logger.info("Started analysis for README file(s) ...")

            if filter_repository_artefacts.get_readme():
                readme_analysis.analyse_readme(verbose)
                logger.info("Finished analysis for README file(s).")
            else:
                # if no readmes are detected/present
                logger.warning('No readme file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No readme(s) detected.[/bold red]')

            # scans found licenses for open-source licenses
            # saves all open-source licenses into list
            # if no match is found assumes that license is not open-source
            logger.info("Started analysis for LICENSE file(s) ...")

            if filter_repository_artefacts.get_license():
                license_analysis.analyse_license(verbose)
                logger.info("Finished analysis for LICENSE file(s).")
            else:
                # if no licenses are detected/present
                logger.warning('No license file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No license(s) detected.[/bold red]')

            if filter_repository_artefacts.get_dataset_folders():
                dataset_analysis.analyse_datasets()
                logger.info("Finished analysis of possible dataset folder(s).")
            else:
                # if no dataset folder(s) are detected/present
                logger.warning('No dataset folder(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No dataset folder(s) detected.[/bold red]')

            if filter_repository_artefacts.get_source_code_files():
                source_code_analysis.analyze_source_code(verbose)
                logger.info("Finished analysis for source code file(s).")
            else:
                # if no source code files are detected/present
                logger.warning('No source code file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No source code file(s) detected.[/bold red]')

            # use data collected from dataset analysis + source code analysis
            dataset_analysis.build_dataset_response(verbose)

            if filter_repository_artefacts.get_config_files():
                config_files_analysis.analyse_config_files(verbose)
                logger.info("Finished analysis for config file(s).")
            else:
                # if no config files are detected/present
                logger.warning('No config file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No config file(s) detected.[/bold red]')

            # builds the repository with BinderHub
            # API call response can either be successful or not
            # TODO: BINDER HUB CALL

            try:
                shutil.rmtree(local_repo_dir)
                logger.info('Removed ' + local_repo_dir + '.')
            except OSError as e:
                logger.error("%s : %s" % (local_repo_dir, e.strerror))

            # brings all the data together
            result_builder.build_result(repository_url, output_file)
            print('\n:thumbs_up: [bold green]Finished repository reproducibility analysis.[/bold green]\n')
        elif opt not in ('-v', '--verbose'):
            logger.error('Use "python3 main.py -h" for help test')

            # TODO: implement feedback builder


if __name__ == '__main__':
    main(sys.argv[1:])

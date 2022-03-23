#!/usr/bin/python3

# possible improvements
# TODO: maybe provide logs also in a persistent log file (additional)
# TODO: MAKE CLEAN UP optional? -> Maybe someone wants to keep the repo locally
# TODO: give user possibility to specify BinderHub himself
# TODO: give user possibility to specify output path himself

import getopt
import logging
import sys
import shutil
import re
from rich import print
import json
from modules import *

# the result and feedback files will be saved under this path
output_path = '/tmp/'
csv_name = 'ml_repo_reproducibility_analyzer'


def main(argv):
    """
        Entry point. Processes the terminal commands and executes each module in the order described in the flowchart
        (see /assets/images/flowchart.png). Skips not relevant module calls e.g. if no readme is present no analysis
        is needed for readme files.

        Parameters:
            argv (List[str]): A list of command-line arguments
    """
    logger = logging.getLogger('log')
    syslog = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    syslog.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(syslog)

    # this banner is just cosmetic. will be shown at the start of this program in the command line.
    banner_text = open("assets/banner.txt")
    lines = banner_text.readlines()

    for line in lines:
        print(line)

    # default: verbose = 0 means no verbose mode. when specified with -v or --verbose additional terminal output
    # will be shown. Useful for debugging.
    verbose = 0
    try:
        opts, args = getopt.getopt(argv, "hvu:", ["help", "url=", "verbose"])
        # if no arguments are provided when calling python3 main.py
        if not opts:
            logger.error('No command specified: Use "python3 main.py -h" for help.')
            sys.exit()
    # if unavailable commands are specified
    except getopt.GetoptError:
        logger.error('Use "python3 main.py -h" for help.')
        sys.exit(2)
    # first loop checks for -h or --help and prints out this table if specified. if not -h or --help but -v or
    # --verbose specified verbose will be on.
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
    # if argument -u or --url provided and no unavailable commands or -h/--help in argv
    # this starts the analysis process
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

            # assuming that the repository is stored on github
            if 'github' not in repository_url:
                logger.error('URL incorrect. Accepted are repositories from github. Use "python3 main.py -h" for help.')
                sys.exit()

            # create output_file if not already there
            output_file = output_path + csv_name + '.csv'
            result_builder.create_csv_file(output_file)

            # checks if repository already analyzed in output file
            if result_builder.check_repository(repository_url, output_file):
                logger.info('Repository ' + repository_url + ' already in result ' + output_file)
                print("\n:smiley: [bold green]Repository already analyzed.[/bold green]\n")
                sys.exit()

            # downloads the repository if it is public and has a master or main branch
            logger.info('Downloading repository ' + repository_url + ' ...')
            local_repo_dir = repository_cloner.clone_repo(repository_url)
            logger.info('Finished downloading ' + repository_url)

            # analysis of the repository structure
            # retrieve relevant artifacts (readmes, licenses, dataset/image folders, source code files, config files,
            # model serialization artifacts and so on)
            print("\n:smiley: [bold green]Started repository analysis ...[/bold green]\n")
            filter_repository_artifacts.get_relevant_artifacts(local_repo_dir, verbose)
            logger.info('Finished detecting relevant repository artifacts.')

            # checks the readmes found for specified attributes
            logger.info("Started analysis for README file(s) ...")

            if filter_repository_artifacts.get_readme():
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

            if filter_repository_artifacts.get_license():
                license_analysis.analyse_license(verbose)
                logger.info("Finished analysis for LICENSE file(s).")
            else:
                # if no licenses are detected/present
                logger.warning('No license file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No license(s) detected.[/bold red]')

            if filter_repository_artifacts.get_dataset_folders() or filter_repository_artifacts.get_files_name_data():
                dataset_analysis.analyse_datasets()
                logger.info("Finished analysis of possible dataset files(s).")
            else:
                # if no dataset folder(s) are detected/present
                logger.warning('No dataset folder(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No dataset folder(s) detected.[/bold red]')

            # stores all dataset files candidates who are also mentioned in the source code
            mentioned_dataset_files_in_sc = []
            logger.info("Started source code file(s) analysis ...")
            if filter_repository_artifacts.get_source_code_files():
                mentioned_dataset_files_in_sc.extend((source_code_analysis.analyze_source_code(verbose)))
                logger.info("Finished analysis for source code file(s).")
            else:
                # if no source code files are detected/present
                logger.warning('No source code file(s) to analyse detected.')
                print(':pile_of_poo: [bold red]No source code file(s) detected.[/bold red]')

            # use data collected from dataset analysis + source code analysis
            dataset_analysis.build_dataset_response(mentioned_dataset_files_in_sc, verbose)

            logger.info("Started analysis for config file(s).")
            config_files_analysis.analyse_config_files(verbose)
            logger.info("Finished analysis for config file(s).")

            # builds the repository with BinderHub
            # API call response can either be successful or not
            print('\n[bold green]Initiating BinderHub build. This may take a while...[/bold green]\n')
            repo_url_lst = repository_url.replace('https://', '').replace('www.', '') \
                .replace('github.com/', '').split('/')
            repo_author = repo_url_lst[0]
            repo_name = repo_url_lst[1]
            # binderhub_call.call_binderhub_to_build(repo_author, repo_name)

            try:
                shutil.rmtree(local_repo_dir)
                logger.info('Removed ' + local_repo_dir + '.')
            except OSError as e:
                logger.error("%s : %s" % (local_repo_dir, e.strerror))

            # brings all the data together
            result_builder.build_result(repository_url, output_file)
            # builds user feedback
            feedback_file_path = output_path + 'feedback-' + csv_name + '.md'
            feedback_builder.build_feedback(feedback_file_path)
            print('\n:thumbs_up: [bold green]Finished repository reproducibility analysis.[/bold green]\n')
        elif opt not in ('-v', '--verbose'):
            logger.error('Use "python3 main.py -h" for help test')


def find_values(id, json_repr):
    results = []

    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict

    json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
    return results


if __name__ == '__main__':
    main(sys.argv[1:])

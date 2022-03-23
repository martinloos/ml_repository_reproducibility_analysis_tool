#!/usr/bin/python3

import logging
import sys
import os
import requests
import git

logger = logging.getLogger('log')


# cloning repository into /tmp/<directory_name>
def clone_repo(url):
    """
        Firstly, it is checked if the repository is already present in the /tmp folder. If not, we try to download
        it (trying master branch first, if not present main branch next, if not present we exit).

        Parameters:
            url (str): The URL of the repository which should be cloned.

        Returns:
            local_dir_path (str): The path where the downloaded repository is stored.
    """
    directory_name = build_name_from_url(url)
    local_dir_path = '/tmp/' + directory_name
    cloning_error = 1

    # check if local_dir_path already used
    if not os.path.isdir(local_dir_path):
        test_repo_url(url)
        # we're accepting master branch or alternatively main branch
        # optimally this section is user input dependent
        try:
            git.Repo.clone_from(url, local_dir_path, branch='master')
            cloning_error = 0
        except git.exc.GitCommandError as exception:
            logger.info('No "master" branch found. Trying "main".')
        if cloning_error == 1:
            try:
                git.Repo.clone_from(url, local_dir_path, branch='main')
                cloning_error = 0
            except git.exc.GitCommandError as exception:
                logger.info('No "main" branch found. At the moment only master and main supported.')
        if cloning_error == 1:
            logger.error('Cloning the repository failed. Please verify your provided URL ' + url)
            sys.exit()
    else:
        logger.error('Local repository path exists already. We assume the repository with the following local path is '
                     'the one you want to analyze: ' + local_dir_path)

    return local_dir_path


def test_repo_url(url):
    try:
        # test if link starts with http or https
        status = requests.get(url).status_code
        if status == 404:
            logger.error('Status code 404. Connecting to the repository failed. Please check if the URL is correct and '
                         'if the repository is public. URL: ' + url)
            sys.exit()
    except requests.ConnectionError as exception:
        logger.error('Connecting to the repository failed. Please check if this URL is correct: ' + url)
        sys.exit()


def build_name_from_url(url):
    # removing everything before the occurrence of the first three '/' from url
    res = url.split('/', 3)[-1]
    # replacing '/' with '-'
    return res.replace('/', '-')

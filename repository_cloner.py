#!/usr/bin/python3

# TODO: doc

import logging
import sys
import os
import requests

import git

logger = logging.getLogger('log')


# cloning repository into /tmp/<directory_name>
def clone_repo(url):
    directory_name = build_name_from_url(url)
    local_dir_path = '/tmp/' + directory_name

    # check if local_dir_path already used

    if not os.path.isdir(local_dir_path):
        try:
            test_repo_url(url)
            git.Repo.clone_from(url, local_dir_path, branch='master')
        except git.exc.GitCommandError as exception:
            logger.error('Cloning the repository failed. Please verify your provided URL ' + url)
            sys.exit()
        return local_dir_path
    else:
        logger.error('Downloading repository failed. Please rename or delete the following directory in order to use '
                     'this tool with the provided url. Directory path: ' + local_dir_path)
        sys.exit()


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

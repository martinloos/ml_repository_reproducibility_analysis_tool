#!/usr/bin/python3

import logging
import os

logger = logging.getLogger('log')
# Stores all the directories which are present in the repository
directory_list = []
# Stores all the files which are present in the repository
file_list = []


def get_structure(root):
    """
        All directories found in the repository are stored into the directory_list. All files found are stored into
        the file_list. Based on this, we build a list containing these lists, which will be returned.

        Parameters:
            root (str): The path to the root of the repository.

        Returns:
            repository_structure (List): A list containing the list of all directories, and the list of all files
            present in the repository.
    """
    for root, dirs, files in os.walk(root):
        for d in dirs:
            # directory_name, path_to_directory, directory_size
            directory_name = d
            directory_path = (os.path.join(root, d))
            directory_size = (os.stat(directory_path)).st_size
            directory_entity = directory_name, directory_path, directory_size
            directory_list.append(directory_entity)
        for f in files:
            # file_name, path_to_file, file_size
            file_name = f
            file_path = (os.path.join(root, f))
            file_size = (os.stat(file_path)).st_size
            file_entity = file_name, file_path, file_size
            file_list.append(file_entity)

    logger.debug('_______________ ALL DIRECTORIES _______________')

    sorted_dlist = sorted(directory_list, key=lambda x: x[-1], reverse=True)
    for element in sorted_dlist:
        logger.debug(element)

    logger.debug('_________________ ALL FILES __________________')

    sorted_flist = sorted(file_list, key=lambda x: x[-1], reverse=True)
    for element in sorted_flist:
        logger.debug(element)

    repository_structure = [sorted_dlist, sorted_flist]

    return repository_structure


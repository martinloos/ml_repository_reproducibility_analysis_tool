# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows,
# actions, and settings.

# TODO: doc

import logging
import os

logger = logging.getLogger('log')

directory_list = []
file_list = []


def get_structure(root):
    for root, dirs, files in os.walk(root):
        for d in dirs:
            # directory_name, path_to_directory, directory_size
            directory_name = d
            directory_path = (os.path.join(root, d))
            directory_size = (os.stat(directory_path)).st_size
            directory_entity = (directory_name, directory_path, directory_size)
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

    return [sorted_dlist, sorted_flist]

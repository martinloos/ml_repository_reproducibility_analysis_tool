#!/usr/bin/python3

import modules.filter_repository_artifacts as filter_repository_artifacts
import modules.dataset_analysis as dataset_analysis
import modules.python_source_code_analysis as python_source_code_analysis
from rich import print
from rich.console import Console
from rich.table import Table
import logging
import subprocess

logger = logging.getLogger('log')
# Stores for each source code file the analysis results
source_code_file_results = []
# Stores the overall result for all the source code files analyzed
source_code_analysis_result = []
# Stores all the unique (duplicates eliminated) source code imports
unique_imports = []
# Stores a list of libs which are not in the python standard library and not local modules but are publicly available
public_libs = []
# Stores a list of libs which are not in the python standard library and not local modules but not publicly available
not_public_libs = []
# file_names and mod_file_paths of each source code file used to filter relevant imports
# we want to exclude local module imports
file_names = []
# list of file paths, but modified. used to detect nested local module imports (e.g. import module.module_name)
mod_file_paths = []
# Stores all the dataset file candidates who are mentioned in at least one source code file
mentioned_dataset_files = []
# excluding libraries below when comparing imports from config file to the used imports from source code
# also excluding imports named like files e.g. import model when there is a model.py file
# we don't expect these libraries to be mentioned in the config files
# according to: https://docs.python.org/3/library/
py_standard_lib_list = ['io', 'os', 'os.path', 'argparse', 'getopt', 'optparse', 'pathlib', 'pickle', 'copyreg',
                        'shelve', 'marshal', 'dbm', 'sqlite3', 'csv', 'configparser', 'netrc', 'xdrlib', 'plistlib',
                        'hashlib', 'hmac', 'secrets', 'shutil', 'glob', 'sys', 'struct', 'threading', 'zipfile',
                        'logging', 'logging.config', 'logging.handlers', 'array', 'collections', 'bisect', 'heapq',
                        'decimal', 'enum', 'graphlib', 're', 'math', 'random', 'numbers', 'fractions', 'statistics',
                        'urllib', 'smtplib', 'datetime', 'zlib', 'gzip', 'bz2', 'lzma', 'tarfile', 'time', 'timeit',
                        'doctest', 'unittest', 'json', 'reprlib', 'pprint', 'textwrap', 'locale', 'string',
                        'ast', 'difflib', 'unicodedata', 'stringprep', 'readline', 'rlcompleter', 'codecs',
                        'datetime', 'zoneinfo', 'calendar', 'collections.abc', 'weakref', 'types', 'copy', 'reprlib',
                        'graphlib', 'cmath', 'intertools', 'functools', 'operator', 'fileinput', 'stat', 'filecmp',
                        'tempfile', 'fnmatch', 'linecache', 'getpass', 'curses', 'curses.textpad', 'curses.ascii',
                        'curses.panel', 'platform', 'errno', 'ctypes', 'multiprocessing',
                        'multiprocessing.shared_memory', 'concurrent', 'concurrent.futures', 'subprocess', 'sched',
                        'queue', 'contextvars', '_thread', 'asyncio', 'socket', 'ssl', 'select', 'selectors',
                        'asyncore', 'asynchat', 'signal', 'mmap', 'email', 'mailcap', 'mailbox', 'mimetypes', 'base64',
                        'binhex', 'binascii', 'quopri', 'uu', 'html', 'html.parser', 'html.entities', 'xml',
                        'xml.etree', 'xml.dom.minidom', 'xml.dom.pulldom', 'xml.sax', 'xml.sax.handlers',
                        'xml.sax.saxutils', 'xml.sax.xmlreader', 'xml.parser.expat', 'webbrowser', 'cgi', 'cgitb',
                        'wsgiref', 'urllib.request', 'urllib.response', 'urllib.parse', 'urllib.error',
                        'urllib.robotparser', 'http', 'http.client', 'ftplib', 'poplib', 'imaplib', 'nntplib',
                        'smtplib', 'smtpd', 'telnetlib', 'uuid', 'socketserver', 'http.server', 'http.cookies',
                        'http.cookiejar', 'xmlrpc', 'xmlrpc.client', 'xmlrpc.server', 'ipaddress', 'audioop', 'aifc',
                        'sunau', 'wave', 'chunk', 'colorsys', 'imghdr', 'sndhdr', 'ossaudiodev', 'gettext', 'turtle',
                        'cmd', 'shlex', 'tkinter', 'tkinter.colorchooser', 'tkinter.font', 'tkinter.messagebox',
                        'tkinter.scrolledtext', 'tkinter.dnd', 'tkinter.ttk', 'tkinter.tix', 'typing', 'pydoc',
                        'doctest', 'unittest', 'unittest.mock', '2to3', 'test', 'test.support',
                        'test.support.socket_helper', 'test.support.script_helper', 'test.support.bytecode_helper',
                        'test.support.threading_helper', 'test.support.os_helper', 'test.support.import_helper',
                        'test.support.warnings_helper', 'bdb', 'faulthandler', 'pdb', 'trace', 'tracemalloc',
                        'distutils', 'ensurepip', 'venv', 'zipapp', 'sysconfig', 'builtins', '__main__', 'warnings',
                        'dataclasses', 'contextlib', 'abc', 'atexit', 'traceback', '__future__', 'gc', 'inspect',
                        'site', 'code', 'codeop', 'zipimport', 'pkgutil', 'modulefinder', 'runpy', 'importlib',
                        'importlib.metadata', 'symtable', 'token', 'keyword', 'tokenize', 'tabnanny', 'pyclbr',
                        'py_compile', 'compileall', 'dis', 'pickletools', 'msilib', 'msvcrt', 'winreg', 'winsound',
                        'posix', 'pwd', 'spwd', 'grp', 'crypt', 'termios', 'tty', 'pty', 'fcntl', 'pipes', 'resource',
                        'nis', 'syslog']
# List of all lib imports in source code that are not in py_standard_lib_list and file_names or mod_file_paths
not_standard_lib_imports = []


def analyze_source_code(verbose):
    """
        Firstly, all found source code files from the filter_repository_artifacts module are collected.
        Then, all the identified dataset file candidates are collected from the dataset_analysis module.
        For each source code file the corresponding module is called (python_source_code_analysis for .py and .ipynb).
        Source_code_file_result stores the analysis result for each source code file. Based on this the overall result
        is created and stored (source_code_analysis_result). This result will also be printed out in the command line.
        If verbose is specified, additional information will be printed out as well.
        Note: At the moment only .py and .ipynb files are supported. Other source code types can be integrated by
        plugging them in here.

        Parameters:
            verbose (int): Default = 0 if verbose (additional command line information) off.

        Returns:
            mentioned_dataset_files (List[str]): A list containing all the dataset file candidates who are mentioned in
            at least one of the source code files.
    """
    source_code_files = filter_repository_artifacts.get_source_code_files()
    dataset_file_candidates = dataset_analysis.get_dataset_file_candidates()
    counter = 1

    for file in source_code_files:
        file_name = file[0]
        file_path = file[1]
        # replace file path '/' with '.' in order to make a string comparison for local modules in folders e.g.:
        # the path could be tmp.model.modules.extraction to filter the import modules.extraction
        mod_f_path = file_path.replace('/', '.')
        mod_file_paths.append(mod_f_path)

        logger.info('Processing source code file ' + str(counter) + ' out of ' + str(len(source_code_files))
                    + ' (' + file_name + ')')
        # add other elif clause to support other source code types
        if 'py' in file_name:
            sc_analysis_result = python_source_code_analysis.python_code_analysis(file_name, file_path,
                                                                                  dataset_file_candidates, verbose)
            source_code_file_results.append(sc_analysis_result)
            # add file name to list in order to be able to filter not relevant local module imports
            f_name = file_name.replace('.py', '').strip()
            file_names.append(f_name)
        counter = counter + 1

    build_source_code_result(verbose)

    return mentioned_dataset_files


def get_file_length(file_path):
    i = 0
    with open(file_path) as r:
        for i, l in enumerate(r):
            pass
    return i + 1


def get_source_code_analysis():
    return source_code_analysis_result


def calculate_percentage(value1, value2):
    return round(100 * float(value1) / float(value2), 2)


def check_for_model_serialization():
    dvc_folder = filter_repository_artifacts.get_dvc_folder()

    if dvc_folder:
        return 1

    ms_files = filter_repository_artifacts.get_ms_files()

    if ms_files:
        return 1


# check if imports used in source code are public available
# requires pip-search to be installed see requirements.txt
def check_if_sc_libs_public():
    for imp in not_standard_lib_imports:
        commands = ['pip_search', imp]

        cmd = subprocess.Popen(commands, stdout=subprocess.PIPE)
        out, err = cmd.communicate()

        dec_out = out.decode('utf-8')
        dec_out_lst = dec_out.split('\n')
        # remove https://pypi.org/search/?q=<package_name> from list. We later check if package name is in list and
        # therefore, we don't want this entry to match
        del dec_out_lst[0]
        # changing value if package name in dec_out_lst
        public = 0
        for line in dec_out_lst:
            if imp.lower() in line.lower():
                public = 1
        if public == 1:
            public_libs.append(imp)
        else:
            not_public_libs.append(imp)


def get_imports():
    return not_standard_lib_imports


def build_source_code_result(verbose):
    number_of_sc_files = len(source_code_file_results)
    total_code_lines = 0
    total_comment_lines = 0
    weighted_pylint_sum = 0
    total_sc_lines = 0
    number_of_jn = 0
    jn_with_header_comment = 0
    jn_with_footer_comment = 0
    number_of_rdm_seed_lines = 0
    number_of_fixed_rdm_seed_lines = 0
    number_of_hyperparameter_doc_indicators = 0
    number_of_model_serialization_indicators = 0

    for result in source_code_file_results:
        total_code_lines = total_code_lines + result[0]
        total_comment_lines = total_comment_lines + result[1]
        total_sc_lines = total_sc_lines + result[3]
        # weighted pylint result (depending on source code lines of file)
        weighted_pylint_sum = weighted_pylint_sum + result[2] * result[3]
        # analyzed source code file was .ipynb file
        if result[6] == 1:
            number_of_jn = number_of_jn + 1
            # .ipynb had header comments
            if not result[4] == 0:
                jn_with_header_comment = jn_with_header_comment + 1
            # .ipynb had footer comments
            if not result[5] == 0:
                jn_with_footer_comment = jn_with_footer_comment + 1
        number_of_rdm_seed_lines = number_of_rdm_seed_lines + result[7]
        number_of_fixed_rdm_seed_lines = number_of_fixed_rdm_seed_lines + result[8]
        number_of_hyperparameter_doc_indicators = number_of_hyperparameter_doc_indicators + result[9]

        # duplicate elimination (multiple sc files)
        for imp in result[10]:
            imp_tmp = imp.replace(',', '')
            if imp_tmp not in unique_imports:
                unique_imports.append(imp_tmp)

        for dataset_file in result[11]:
            if dataset_file not in mentioned_dataset_files:
                mentioned_dataset_files.append(dataset_file)

        number_of_model_serialization_indicators = number_of_model_serialization_indicators + result[12]

    # eliminating imports from python standard library
    for imp in unique_imports:
        lib_imp_is_nested_module_path = 0

        # if imp is nested module path e.g. path: model.modules.f_extraction and imp: modules.f_extraction
        # example two: from modules import xy -> imp = modules -> modules is in mod_f_path -> locale
        if '.' in imp:
            for mod_f_path in mod_file_paths:
                if imp in mod_f_path:
                    lib_imp_is_nested_module_path = 1

        # if imp is not nested module path check if it is not nested local module import or in python standard libraries
        if lib_imp_is_nested_module_path == 0:
            tmp_imp = imp

            # remove '.' so that e.g. torch.xy and torch are the same
            if '.' in imp:
                tmp_imp = imp.split('.')[0]
            # if this is the case add imp to the list
            if (tmp_imp not in py_standard_lib_list) and (tmp_imp not in file_names) and \
                    (tmp_imp not in not_standard_lib_imports):
                not_standard_lib_imports.append(tmp_imp)

    # calculate how many of the in the source code used (excluding python standard and local libraries) libs are public
    percentage_public_sc_libs = 0

    if not_standard_lib_imports:
        check_if_sc_libs_public()

    if public_libs:
        percentage_public_sc_libs = calculate_percentage(len(public_libs), len(not_standard_lib_imports))

    percentage_code_lines = calculate_percentage(total_code_lines, total_sc_lines)
    percentage_comment_lines = calculate_percentage(total_comment_lines, total_sc_lines)
    average_pylint_score = round(weighted_pylint_sum / total_sc_lines, 2)

    # > 1 means there is more code lines than comment lines
    if total_comment_lines > 0:
        code_comment_ratio = round(total_code_lines / total_comment_lines, 2)
    else:
        code_comment_ratio = total_code_lines

    average_jn_header_comment = 0
    average_jn_footer_comment = 0

    if number_of_jn > 0:
        average_jn_header_comment = calculate_percentage(jn_with_header_comment, number_of_jn)
        average_jn_footer_comment = calculate_percentage(jn_with_footer_comment, number_of_jn)

    percentage_fixed_rdm_seed = 0

    if number_of_rdm_seed_lines > 0:
        percentage_fixed_rdm_seed = calculate_percentage(number_of_fixed_rdm_seed_lines, number_of_rdm_seed_lines)

    model_serialization_used = 'No'
    # if model serialization -> number of hyperparameter indicators irrelevant because models are serialized
    if (check_for_model_serialization() == 1) or (number_of_model_serialization_indicators > 0):
        model_serialization_used = 'Yes'

    source_code_analysis_result.extend((number_of_sc_files, total_code_lines, percentage_code_lines,
                                        total_comment_lines, percentage_comment_lines, code_comment_ratio,
                                        average_pylint_score, number_of_jn, average_jn_header_comment,
                                        average_jn_footer_comment, number_of_rdm_seed_lines, percentage_fixed_rdm_seed,
                                        model_serialization_used, number_of_hyperparameter_doc_indicators,
                                        percentage_public_sc_libs))

    console = Console()

    print('\n\n')
    print('[bold] _______________________________________________________[/bold]')
    print('[bold]|[magenta]                   SOURCE CODE ANALYSIS                [/magenta]|[/bold]')
    print('[bold]|_______________________________________________________|[/bold]\n')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# source code files', str(number_of_sc_files))
    table.add_row('# total lines of code', str(total_code_lines))
    table.add_row('% of code lines', str(percentage_code_lines))
    table.add_row('# total comment lines', str(total_comment_lines))
    table.add_row('% of comment lines', str(percentage_comment_lines))
    table.add_row('code-comment-ratio', str(code_comment_ratio))
    table.add_row('average pylint score (best is 10)', str(average_pylint_score))
    table.add_row('# jupyter notebooks', str(number_of_jn))
    table.add_row('% of jupyter notebooks /w header', str(average_jn_header_comment))
    table.add_row('% of jupyter notebooks /w footer', str(average_jn_footer_comment))
    table.add_row('# random seed lines', str(number_of_rdm_seed_lines))
    table.add_row('% fixed random seed lines', str(percentage_fixed_rdm_seed))
    table.add_row('Model serialization used?', model_serialization_used)
    table.add_row('# hyperparameter logging indicators', str(number_of_hyperparameter_doc_indicators))
    table.add_row('% public available libraries in relation to all unique imports in source code (excl. local '
                  'and python standard libs)' + str(percentage_public_sc_libs))
    console.print(table)
    print('\n')

    # if verbose specified in terminal command prints out additional information
    if verbose == 1:

        if public_libs:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("PUBLICLY AVAILABLE LIBRARIES (who are used in the source-code and aren't standard python "
                             "libraries or not in repository)", justify="left")
            for lib in public_libs:
                table.add_row(lib)
            console.print(table)
            print('\n')

        if not_public_libs:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("NOT PUBLICLY AVAILABLE LIBRARIES (who are used in the source-code and aren't standard "
                             "python libraries or not in repository)", justify="left")
            for lib in not_public_libs:
                table.add_row(lib)
            console.print(table)
            print('\n')

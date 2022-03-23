#!/usr/bin/python3

import os
import re
from pylint import epylint as lint
from io import StringIO
from rich import print
from rich.console import Console
from rich.table import Table


def python_code_analysis(file_name, file_path, dataset_candidates, verbose):
    """
        Firstly, it is checked if the python source code file has the .ipynb extension. If yes, it is converted into a
        .py file using nbconvert. Then, the .py file is processed line by line. All comment, code and import lines are
        each stored in a separate list. For code lines we also check if a random seed is declared in the current line
        or if one of the dataset_candidates is mentioned. For all the import lines we check whether hyperparameter
        logging relevant imports are made. For all the code lines we check whether hyperparameter logging relevant code
        is declared. If yes, these are stored into lists. Also, the pylint rating is calculated for the .py file using
        pylint. Further statistical measurements are taken.

        Parameters:
            file_name (str): The name of the python source code file.
            file_path (str): The path to the python source code file.
            dataset_candidates (List[str]): A list of all the possible dataset files.
            verbose (int): Default = 0 if verbose (additional command line information) off.

        Returns:
            analysis_result (List): A list with all the measured analysis entries.
    """
    f_name = file_name
    file_directory = get_file_directory(file_path)
    os.chdir(file_directory)
    is_jupyter_notebook = 0

    if '.ipynb' in file_name:
        f_name = convert_jupyter_nb_to_py(file_name)
        is_jupyter_notebook = 1

    file = file_directory + '/' + f_name

    source_code = open(file, "r")
    sc_lines = source_code.readlines()
    source_code.close()

    comment_lines = []
    code_lines = []
    import_lines = []
    mentioned_dataset_candidates = []

    # TODO: Strategy how to evaluate header + footer further?
    # NOTE COMMENT LINES BEFORE FIRST CODE LINE
    header_comment = 0
    header_comment_present = 'true'
    header_comments = []

    # NOTE COMMENT LINES AFTER THE LAST PIECE OF CODE
    footer_comment = 0
    footer_comments = []

    multiple_comment_line = 0

    fixed_random_seed_lines = []
    unfixed_random_seed_lines = []

    for l in sc_lines:
        if not l.isspace():
            line = l.strip()
            # comment line case 1: not start/end of multiline comment but comment line
            if ((multiple_comment_line == 1) and not (('"""' in line) or ("'''" in line))) or (line[:1] == '#'):
                comment = parse_comment_line(line)
                if comment:
                    comment_lines.append(comment)
                    # after reading the first code line is not true anymore
                    if header_comment_present == 'true':
                        header_comments.append(comment)
                    # will be cleared if next line is not comment line
                    footer_comments.append(comment)
            # comment line case 2: possible multiline comment
            elif ('"""' in line) or ("'''" in line):
                if '"""' in line:
                    line_tmp = line.replace('"""', '', 1)
                    # start/end of multiple line comment e.g. """xyz OR xyz """
                    if '"""' not in line_tmp:
                        # start of multi comment line
                        if multiple_comment_line == 0:
                            multiple_comment_line = 1
                        # end of multi comment line
                        else:
                            multiple_comment_line = 0
                elif "'''" in line:
                    line_tmp = line.replace("'''", "", 1)
                    # start/end of multiple line comment e.g. '''xyz OR xyz '''
                    if "'''" not in line_tmp:
                        # start of multi comment line
                        if multiple_comment_line == 0:
                            multiple_comment_line = 1
                        # end of multi comment line
                        else:
                            multiple_comment_line = 0
                # in all cases this is a comment line """xyz""" or '''xyz''' or '''xyz or xyz''' or """xyz or xyz"""
                comment = parse_comment_line(line)
                if comment:
                    comment_lines.append(comment)
                    # after reading the first code line is not true anymore
                    if header_comment_present == 'true':
                        header_comments.append(comment)
                    # will be cleared if next line is not comment line
                    footer_comments.append(comment)
            elif line.split()[0] in ('from', 'import'):
                imp = parse_import_line(line)
                if imp:
                    if imp not in import_lines:
                        import_lines.append(imp)
            else:
                code_line = parse_code_line(line)
                random_seed_line = check_for_random_seed(code_line)

                if random_seed_line == 1:
                    fixed_random_seed_lines.append(code_line)

                if random_seed_line == 2:
                    unfixed_random_seed_lines.append(code_line)

                # check if one of the dataset candidates is mentioned in this line of code
                mentioned_dataset_candidates = check_dataset_candidates(code_line, dataset_candidates,
                                                                        mentioned_dataset_candidates)

                code_lines.append(code_line)
                header_comment_present = 'processed'
                if footer_comments:
                    footer_comments.clear()

    if header_comments:
        header_comment = len(header_comments)

    if footer_comments:
        footer_comment = len(footer_comments)

    hp_import_indicators = check_import_hyperparameter_indicators(import_lines)
    hp_logging_ind = check_code_hyperparameter_indicators(code_lines, hp_import_indicators)

    # number of found imports and logging usages that possibly correlate to hyperparameter logging
    number_of_hp_doc_indicator = len(hp_import_indicators) + len(hp_logging_ind)

    # code lines that include indicators of model serialization declarations
    ms_indicators = check_code_model_serialization_indicators(code_lines)

    # number of model serialization code lines
    number_of_ms_indicator = len(ms_indicators)

    pylint_rating = pylint_code_style_rating(f_name, file, verbose)

    number_of_comment_lines = len(comment_lines)
    number_of_code_lines = len(code_lines) + len(import_lines)
    total_sc_lines = number_of_comment_lines + number_of_code_lines

    number_of_fixed_random_seed_lines = len(fixed_random_seed_lines)
    number_of_random_seed_lines = number_of_fixed_random_seed_lines + len(unfixed_random_seed_lines)

    # if verbose specified in terminal command prints out additional information
    if verbose == 1:
        build_feedback(code_lines, comment_lines, import_lines, number_of_code_lines, number_of_comment_lines,
                       f_name, file, pylint_rating, fixed_random_seed_lines, unfixed_random_seed_lines,
                       hp_import_indicators, hp_logging_ind, ms_indicators)

    analysis_result = [number_of_code_lines, number_of_comment_lines, pylint_rating, total_sc_lines, header_comment,
                       footer_comment, is_jupyter_notebook, number_of_random_seed_lines,
                       number_of_fixed_random_seed_lines, number_of_hp_doc_indicator, import_lines,
                       mentioned_dataset_candidates, number_of_ms_indicator]

    return analysis_result


# removing file name
def get_file_directory(file_path):
    idx = file_path.rfind("/")
    if idx >= 0:
        file_path = file_path[:idx]
    return file_path


def convert_jupyter_nb_to_py(file_name):
    f_name = re.sub(r"[^a-zA-Z0-9.]", "", file_name)
    os.rename(file_name, f_name)
    os.system('jupyter nbconvert ' + str(f_name) + ' --to python')
    f_name = f_name.replace('.ipynb', '.py')
    return f_name


def parse_comment_line(comment_line):
    # jupyter notebook artefact, not an actual comment
    if '# In[' in comment_line:
        return
    if '!/usr/bin/env' in comment_line:
        return

    comment = comment_line.replace('#', '').replace('"""', '').replace("'''", "")
    comment = comment.replace('\n', '')
    return remove_leading_whitespace(comment)


def parse_import_line(import_line):
    imp = remove_leading_whitespace(import_line).split()[1]

    # problem: found import .xy in sc and xy in config file
    if (imp.startswith('.')) and (len(imp) > 1):
        imp = imp.replace('.', '', 1)

    return imp


def parse_code_line(code_line):
    code = remove_leading_whitespace(code_line)
    return code.replace('\n', '')


# returns 1 if random seed found + value fixed
# returns 2 if random seed found but no value fixed (value = none)
# otherwise 0
def check_for_random_seed(code_line):
    # matches e.g. tf.random.set_seed(seed), set_random_seed(2), np.random.seed(10) or torch.manual_seed(opt.manualSeed)
    reg_seed = re.compile(".*?seed.*?\\(.+\\)")
    # matches e.g. tf.random.set_seed(none), set_random_seed(NONE), np.random.seed(None) or torch.manual_seed(None)
    neg_reg_seed = re.compile(".*?seed.*?\\(none\\)")

    # matches e.g. (X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_frac, random_state=42)
    # or also rng = np.random.RandomState(0)', 'coef=True, random_state=0
    reg_rdm_state = re.compile(".*?random(_)?state(\\.)?[^\\w]?(\\(|=)(.+)?(\\))?")
    # matches e.g. (X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_frac, random_state= None )
    # or also rng = np.random.RandomState(None)', 'coef=True, random_state = None
    neg_rdm_state = re.compile(".*?random(_)?state(\\.)?[^\\w]?(\\(|=)(\\s+)?none(\\))?")

    code_line = code_line.lower()

    if bool(re.match(neg_reg_seed, code_line)):
        # found seed declaration + no fixed seed
        return 2
    elif bool(re.match(reg_seed, code_line)):
        # found seed declaration + fixed seed
        return 1
    elif bool(re.match(neg_rdm_state, code_line)):
        # found rdm state declaration + no fixed random state
        return 2
    elif bool(re.match(reg_rdm_state, code_line)):
        # found rdm state declaration + fixed random state
        return 1
    else:
        # no declaration found
        return 0


def check_dataset_candidates(code_line, dataset_candidates, mentioned_dataset_candidates):
    for candidate in dataset_candidates:
        if candidate in code_line:
            if candidate not in mentioned_dataset_candidates:
                mentioned_dataset_candidates.append(candidate)

    return mentioned_dataset_candidates


# checking for hyperparameter logging relevant libraries and code lines
# atm just checking existence not quality or quantity
def check_import_hyperparameter_indicators(imp_lines):
    # checking for wandb, neptune, sacred and mlflow imports
    # these imports enable hyperparameter logging
    hp_relevant_imports = []

    for imp_line in imp_lines:
        if 'wandb' in imp_line:
            hp_relevant_imports.append(imp_line)
        if 'neptune' in imp_line:
            hp_relevant_imports.append(imp_line)
        if 'sacred' in imp_line:
            hp_relevant_imports.append(imp_line)
        if 'mlflow' in imp_line:
            hp_relevant_imports.append(imp_line)

    return hp_relevant_imports


# checking for hyperparameter logging
# atm just checking existence not quality or quantity
def check_code_hyperparameter_indicators(code_lines, hp_imp_ind):
    # checking for typical hyperparameter logging method calls
    hp_relevant_logging = []

    # matches e.g. wandb.config.epochs = 4, wandb.config.batch_size = 32 or wandb.init(config={"epochs": 4})
    reg_wandb_log = re.compile("wandb.(config|init)(.+)?")

    # matches e.g. the following: run['parameters'] = params,
    # run = neptune.init(project=' stateasy005/iris',api_token='', source_files=['*.py', 'requirements.txt']) or
    # run["cls_summary "] = npt_utils.create_classifier_summary(clf, X_train, X_test, y_train, y_test)
    reg_neptune_log = re.compile("run(.+)?=")

    # matches @ex.capture annotation
    reg_sacred_log = re.compile("(.*)?@ex.capture(.*)?")

    # matches e.g. mlflow.log_param("x", 1), mlflow.autolog(), mlflow.sklearn.autolog() or mlflow.XY.autolog()
    reg_mlflow_log = re.compile("mlflow.(.*)?log")

    # adding code line to list of hp relevant logging if one of the regs match
    for code_line in code_lines:
        if bool(re.match(reg_wandb_log, code_line)):
            hp_relevant_logging.append(code_line)
        # extra condition because regex is not perfect and might match things like runtime ... which we don't want
        # extra condition len(hp_imp_ind) reduces false positives
        elif (bool(re.match(reg_neptune_log, code_line))) and (len(hp_imp_ind) > 0):
            hp_relevant_logging.append(code_line)
        elif bool(re.match(reg_sacred_log, code_line)):
            hp_relevant_logging.append(code_line)
        elif bool(re.match(reg_mlflow_log, code_line)):
            hp_relevant_logging.append(code_line)

    return hp_relevant_logging


def check_code_model_serialization_indicators(code_lines):
    ms_indicators = []

    # matches e.g. torch.save(model.state_dict(), PATH), torch.save(model, PATH) or
    # torch.save({'epoch': epoch, 'model_state_dict': model.state_dict(), 'loss': loss, ...}, PATH)
    reg_torch_ms = re.compile("torch.save(.+)?")

    # matches e.g. s = pickle.dumps(clf) or dump(clf, 'filename.joblib')
    reg_pickle_joblib_ms = re.compile("((.*)?pickle.dump(.+)?|(.*)?dump(.+)?joblib(.+)?)")

    # adding code line to list of model serialization indicator if one of the regs match
    for code_line in code_lines:
        if bool(re.match(reg_torch_ms, code_line)):
            ms_indicators.append(code_line)
        elif bool(re.match(reg_pickle_joblib_ms, code_line)):
            ms_indicators.append(code_line)

    return ms_indicators


def pylint_code_style_rating(file, file_path, verbose):
    # ignoring "Unable to import '<library>' (import-error)"
    file_tmp = file
    if ' ' in file:
        file_tmp = file.replace(' ', '\ ')
    (pylint_stdout, pylint_stderr) = lint.py_run(file_tmp + ' --disable E0401', return_std=True)
    stdout = StringIO.getvalue(pylint_stdout).splitlines()
    stderr = StringIO.getvalue(pylint_stderr).splitlines()

    # print additional information to console if verbose mode
    if verbose == 1:
        print('\n:crossed_fingers: [bold magenta] Result of pylint analysis of ' + file + '. Path to file: '
              + file_path + '[/bold magenta]\n')
        print(stdout)
        if stderr:
            print(stderr)

    # 3rd last element of stdout is the string with the rating result
    # returns retrieved pylint rating (ranging from -10 to 10)
    if stdout:
        rating_sentence = (stdout[-3])
        rs_list = rating_sentence.split()
        if len(rs_list) >= 7:
            try:
                rating = float(rs_list[6].split('/')[0])
                return rating
            # occurs e.g. if all code is commented out in source code file
            except ValueError:
                return 0
        return 0
    # if no rating
    else:
        return 0


def remove_leading_whitespace(line):
    return re.sub(r"^\s+", "", line)


def build_feedback(code_lines, comment_lines, imp_lines, number_of_code_lines, number_of_comment_lines,
                   file_name, file_path, pylint_rating, fixed_rdm_seed_lines, unfixed_rdm_seed_lines,
                   hp_import_indicators, hp_code_indicators, ms_indicators):
    # > 1 means there is more code lines than comment lines
    if number_of_comment_lines > 0:
        code_comment_ratio = round(number_of_code_lines / number_of_comment_lines, 2)
    else:
        code_comment_ratio = number_of_code_lines
    console = Console()

    print('\n:detective: [bold magenta] Result of source code analysis of ' + file_name + '. Path to file: '
          + file_path + '[/bold magenta]\n')
    print('[bold red]SOURCE CODE ANALYSIS FOR FILE: ' + file_name + '[/bold red]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("property", justify="left")
    table.add_column("value", justify="right")
    table.add_row('# code lines:', str(number_of_code_lines))
    table.add_row('# comment lines', str(number_of_comment_lines))
    table.add_row('Code-comment-ratio', str(code_comment_ratio))
    table.add_row('Pylint rating', str(pylint_rating))
    console.print(table)
    print('\n')

    # TODO: remove commented out lines below IF you want to print out all the code and comment lines for each python
    # TODO: source code file. commented out, because of massive overhead when analyzing big repositories.
    # print additional information to console if verbose mode
    # if code_lines:
    #    table = Table(show_header=True, header_style="bold green")
    #    table.add_column("SOURCE CODE LINES", justify="left")
    #    for code_line in code_lines:
    #        table.add_row(code_line)
    #    console.print(table)
    #    print('\n')

    # if comment_lines:
    #    table = Table(show_header=True, header_style="bold green")
    #    table.add_column("SOURCE CODE COMMENTS", justify="left")
    #    for comment in comment_lines:
    #        table.add_row(comment)
    #    console.print(table, markup=False)
    #    print('\n')

    if imp_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("SOURCE CODE IMPORTS", justify="left")
        for import_line in imp_lines:
            table.add_row(import_line)
        console.print(table)
        print('\n')

    if fixed_rdm_seed_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("FIXED RANDOM SEED LINES", justify="left")
        for line in fixed_rdm_seed_lines:
            table.add_row(line)
        console.print(table)
        print('\n')

    if unfixed_rdm_seed_lines:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("UNFIXED RANDOM SEED LINES", justify="left")
        for line in unfixed_rdm_seed_lines:
            table.add_row(line)
        console.print(table)
        print('\n')

    if hp_import_indicators:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("INDICATORS OF HYPERPARAMETER LOGGING: IMPORT LINES", justify="left")
        for indicator in hp_import_indicators:
            table.add_row(indicator)
        console.print(table)
        print('\n')

    if hp_code_indicators:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("INDICATORS OF HYPERPARAMETER LOGGING: CODE LINES", justify="left")
        for indicator in hp_code_indicators:
            table.add_row(indicator)
        console.print(table)
        print('\n')

    if ms_indicators:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("INDICATORS OF MODEL SERIALIZATION IN CODE LINES", justify="left")
        for indicator in ms_indicators:
            table.add_row(indicator)
        console.print(table)
        print('\n')

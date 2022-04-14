#!/usr/bin/python3

from rich import print
from rich.console import Console
from rich.table import Table
import modules.result_builder as result_builder

# Stores the result for all factors
factor_result = []
# For factors where the values can be between 1 or 0 we give additional feedback wether it is rather a good or bad score
factor_context = []
# Each list stores the feedback for the corresponding factor
sc_feedback = []
se_feedback = []
ds_feedback = []
rs_feedback = []
ms_feedback = []
hp_feedback = []
bh_feedback = []

# representative values (min(d) and max(d)) and weights extracted like described in the paper (chapter 6 implementation)
# readme min(d) and max(d) for length and accessible links
MIN_D_README_LENGTH = 18
MAX_D_README_LENGTH = 82
MIN_D_ACC_README_LINKS = 1
MAX_D_ACC_README_LINKS = 4
# readme weights
README_LENGTH_WEIGHT = 0.8
ACC_README_LINKS_WEIGHT = 0.2
# overall readme weight
README_WEIGHT = 0.5
# license weight (min(d) and max(d) not needed because all the licenses should be open-source + at least one present)
LICENSE_WEIGHT = 0.3
# code comment ratio min(d), max(d) and weight. computed as 1 - range normalized value because a high ratio is not good
MIN_D_CODE_COMMENT_RATIO = 8.73
MAX_D_CODE_COMMENT_RATIO = 17.46
CODE_COMMENT_RATIO_WEIGHT = 0.1
# pylint rating min(d), max(d) and weight
MIN_D_PYLINT_RATING = 0
MAX_D_PYLINT_RATING = 5.71
PYLINT_RATING_WEIGHT = 0.1
# configuration file min(d) and max(d) for source code imports in conf file, strict dependency declarations in
# conf file and publicly accessible used libraries in source code (all percentage values)
MIN_D_SC_IMP_IN_CONF = 0
MAX_D_SC_IMP_IN_CONF = 100
MIN_D_STRICT_DEPENDENCIES = 0
MAX_D_STRICT_DEPENDENCIES = 100
MIN_D_PUB_ACC_LIBS_IN_SC = 0
MAX_D_PUB_ACC_LIBS_IN_SC = 100
# configuration file weights
SC_IMP_IN_CONF_WEIGHT = 0.6
STRICT_DEPENDENCIES_WEIGHT = 0.2
PUB_ACC_LIBS_IN_SC_WEIGHT = 0.2
# Different thresholds to assess whether a repository complies with the guidelines or not
# not needed for DSA&P as well as MS, HP logging and OOTBB as these values can either be 0 or 1
# MID_ values are the average of the POS_ and NEG_ values
TOP_SCAD_THLD = 0.8
AVG_SCAD_THLD = 0.54
LOW_SCAD_THLD = 0.28
TOP_SE_THLD = 0.61
AVG_SE_THLD = 0.46
LOW_SE_THLD = 0.31
TOP_RS_THLD = 0.94
AVG_RS_THLD = 0.51
LOW_RS_THLD = 0.51


def build_feedback(feedback_file_path):
    """
        Builds the user feedback based on the overall analysis_result. For each factor the corresponding identifiers
        are analyzed. As the value ranges can be quite different we use range normalization to bring them in the same
        range in order to be able to compare them. As the influence of each identifier on the factor is different we
        also use weights for computing a factor score. A full explanation on this is available in the thesis.pdf file.

        Parameters:
            feedback_file_path (str): The path where the feedback markdown file will be stored.
    """
    analysis_result = result_builder.get_analysis_result()

    sc_val = source_code_availability_documentation_feedback(analysis_result)
    se_val = software_environment_feedback(analysis_result)
    ds_val = dataset_availability_preprocessing_feedback(analysis_result)
    rs_val = random_seed_feedback(analysis_result)
    ms_val = model_serialization_feedback(analysis_result)
    hp_val = hyperparameter_feedback(analysis_result)
    bh_val = out_of_the_box_buildability_feedback(analysis_result)

    build_factor_context(sc_val, se_val, ds_val, rs_val, ms_val, hp_val, bh_val)

    build_feedback_file(feedback_file_path)

    print_reproducibility_factor_feedback(sc_val, se_val, ds_val, rs_val, ms_val, hp_val, bh_val)


def source_code_availability_documentation_feedback(analysis_result):
    # processing license
    nbr_licenses = analysis_result[9]
    # ranging from 0 to nbr_licenses
    nbr_os_licenses = analysis_result[10]
    # min(d) is 0 and max(d) is number of licenses as all of them should be open source
    license_value = calculate_license_value(nbr_licenses, nbr_os_licenses)
    weighted_license_value = round(license_value * LICENSE_WEIGHT, 2)

    # processing readme
    readme_value = calculate_readme_value(analysis_result)
    weighted_readme_value = round(readme_value * README_WEIGHT, 2)

    # processing pylint scoring
    # should be more generalised for other source code types
    avg_pylint_score = analysis_result[18]

    pylint_value = range_normalization(avg_pylint_score, MIN_D_PYLINT_RATING, MAX_D_PYLINT_RATING, 0, 1)

    sc_feedback.append('3. Source-code pylint scoring (score: '
                       + str(round(pylint_value, 2))
                       + ' out of 1.0): Not normalized pylint rating is '
                       + str(round(avg_pylint_score, 2))
                       + ' where 10.0 is best. We found that readable code is best for reproducibility and consider '
                         'ratings over ' + str(MAX_D_PYLINT_RATING) + ' as desirable.\n')

    weighted_pylint_value = round(pylint_value * PYLINT_RATING_WEIGHT, 2)

    # processing code comment ratio
    code_comment_ratio = analysis_result[17]

    # 1 - method result because of if code comment ratio is high there are less comment lines per code line
    # that (usually) means a not well code documentation
    code_comment_ratio_value = (1 - range_normalization(code_comment_ratio, MIN_D_CODE_COMMENT_RATIO,
                                                        MAX_D_CODE_COMMENT_RATIO, 0, 1))
    weighted_code_comment_ratio_value = round(code_comment_ratio_value * CODE_COMMENT_RATIO_WEIGHT, 2)

    sc_feedback.append('4. Source-code-comment-ratio scoring (score: '
                       + str(round(code_comment_ratio_value, 2))
                       + ' out of 1.0): We measured a average ratio of '
                       + str(code_comment_ratio) + '. We consider a ratio below '
                       + str(MIN_D_CODE_COMMENT_RATIO) + ' as best. But more comments are fine too (which would make '
                                                         'the ratio smaller). Well documented code is important.\n')

    sc_feedback.append('> Source-code availability and documentation is calculated from the above identifiers. '
                       'Since these have a different influence on the overall result, they are weighted as follows:\n\n'
                       + '- License weight: ' + str(LICENSE_WEIGHT) + '\n'
                       + '- Readme weight: ' + str(README_WEIGHT) + '\n'
                       + '- Sub-readme: Length weight: ' + str(README_LENGTH_WEIGHT) + '\n'
                       + '- Sub-readme: Average accessible links weight: ' + str(ACC_README_LINKS_WEIGHT) + '\n'
                       + '- Pylint rating weight: ' + str(PYLINT_RATING_WEIGHT) + '\n'
                       + '- Code-comment-ratio weight: ' + str(CODE_COMMENT_RATIO_WEIGHT))

    sc_availability_documentation_value = round(weighted_license_value + weighted_readme_value + weighted_pylint_value
                                                + weighted_code_comment_ratio_value, 2)

    return sc_availability_documentation_value


def calculate_license_value(nbr_licenses, nbr_os_licenses):
    if nbr_licenses > 0:
        normalized_license_value = round(range_normalization(nbr_os_licenses, 0, nbr_licenses, 0, 1), 2)
    else:
        # if no license present value is 0 because it should always be one present
        normalized_license_value = 0

    if nbr_licenses == 0:
        sc_feedback.append('1. License scoring (score: '
                           + str(normalized_license_value)
                           + ' out of 1.0): No license information found. Providing a licenses helps others to tell if '
                             'your project and its dependencies are available to them.\n')
    elif nbr_os_licenses == 0:
        sc_feedback.append('1. License scoring (score: '
                           + str(normalized_license_value)
                           + ' out of 1.0): All found licenses are not open-source. Using open-source dependencies '
                             'enables others to use them also.\n')
    elif nbr_licenses != nbr_os_licenses:
        sc_feedback.append('1. License scoring (score: '
                           + str(normalized_license_value)
                           + ' out of 1.0): '
                           + str((nbr_licenses - nbr_os_licenses))
                           + ' of the '
                           + str(nbr_licenses)
                           + ' found licenses are not open-source. Using open-source dependencies enables others to '
                             'use them also.\n')
    else:
        sc_feedback.append('1. License scoring (score: '
                           + str(normalized_license_value)
                           + ' out of 1.0): All found licenses are open-source.\n')

    return normalized_license_value


def calculate_readme_value(analysis_result):
    nbr_readmes = analysis_result[1]
    sc_feedback_queue = []

    if nbr_readmes > 0:
        avg_readme_length = analysis_result[3]

        avg_readme_length_value = round(range_normalization(avg_readme_length, MIN_D_README_LENGTH,
                                                            MAX_D_README_LENGTH, 0, 1) * README_LENGTH_WEIGHT, 2)

        sc_feedback_queue.append('- Average length scoring (score: '
                                 + str(round(avg_readme_length_value / README_LENGTH_WEIGHT, 2))
                                 + ' out of 1.0): We determined that '
                                 + str(MAX_D_README_LENGTH)
                                 + ' or more lines are best. We found '
                                 + str(avg_readme_length)
                                 + ' lines (in average) in the README file(s)')

        pct_not_acc_links = analysis_result[7]
        pct_acc_links = 100 - pct_not_acc_links
        readme_links = analysis_result[4]
        avg_acc_readme_links = (readme_links * pct_acc_links) / (nbr_readmes * 100)

        avg_acc_readme_links_value = round(range_normalization(avg_acc_readme_links, MIN_D_ACC_README_LINKS,
                                                               MAX_D_ACC_README_LINKS, 0, 1)
                                           * ACC_README_LINKS_WEIGHT, 2)

        sc_feedback_queue.append('- Average accessible links scoring (score: '
                                 + str(round(avg_acc_readme_links_value / ACC_README_LINKS_WEIGHT, 2))
                                 + ' out of 1.0): We determined that '
                                 + str(MAX_D_ACC_README_LINKS)
                                 + ' or more links are best. We found '
                                 + str(avg_acc_readme_links)
                                 + ' accessible links (in average) in the README file(s)')

        readme_value = avg_readme_length_value + avg_acc_readme_links_value

        sc_feedback.append('2. README overall scoring (score: '
                           + str(round(readme_value, 2))
                           + ' out of 1.0): See sub-ratings for more information.\n')

        sc_feedback.extend(sc_feedback_queue)
        return readme_value
    # if no readme
    else:
        sc_feedback.append('2. README scoring (score: 0 out of 1.0): No README file(s) found. '
                           'You should add one to document your repository. We expect from a good README to have at '
                           'least ' + str(MAX_D_README_LENGTH) + ' lines. Make sure to also add useful links e.g. a '
                                                                 'paper link. We determined that '
                           + str(MAX_D_ACC_README_LINKS) + ' or more accessible links are best. Make also sure that '
                                                           'all provided links are correct and reachable. Also add a '
                                                           'binder badge if possible '
                                                           '(see out-of-the-box buildability feedback.)\n')
        return 0


def software_environment_feedback(analysis_result):
    nbr_config_files = analysis_result[27]
    # how many relevant imports are in the source code
    nbr_imports_in_sc = analysis_result[30]
    # how many imports are declared in the configuration file(s)
    nbr_imports_in_config = analysis_result[29]
    # default values
    mentioned_to_all_used_val = 0
    strict_declarations_in_config_val = 0

    # config file present and relevant source code imports also
    if (nbr_config_files > 0) and (nbr_imports_in_sc > 0):
        # check how many of the used libs are inside the config files
        pct_mentioned_to_all_used = analysis_result[33]
        # relation: all config libs used in the source code in relation to all source-code libs
        mentioned_to_all_used_val = round(range_normalization(pct_mentioned_to_all_used, MIN_D_SC_IMP_IN_CONF,
                                                              MAX_D_SC_IMP_IN_CONF, 0, 1) \
                                          * SC_IMP_IN_CONF_WEIGHT, 2)

        se_feedback.append('1. Libraries used in the source-code and mentioned in config file scoring '
                           '(score: '
                           + str(mentioned_to_all_used_val)
                           + ' out of ' + str(SC_IMP_IN_CONF_WEIGHT) + '): We found that '
                           + str(pct_mentioned_to_all_used)
                           + '% of the used libraries are defined in the config file(s). We expect that '
                           + str(MAX_D_SC_IMP_IN_CONF) + '% of the in the source-code used relevant libraries are'
                                                         ' defined in the config file(s).\n')

        # check how many of the declarations are version strict
        pct_strict_declarations_in_config = analysis_result[31]
        strict_declarations_in_config_val = round(range_normalization(pct_strict_declarations_in_config,
                                                                      MIN_D_STRICT_DEPENDENCIES,
                                                                      MAX_D_STRICT_DEPENDENCIES,
                                                                      0, 1) * STRICT_DEPENDENCIES_WEIGHT, 2)

        se_feedback.append('2. Strictly defined libraries in config file(s) scoring (score: '
                           + str(strict_declarations_in_config_val)
                           + ' out of ' + str(STRICT_DEPENDENCIES_WEIGHT) + '): We expect that '
                           + str(MAX_D_STRICT_DEPENDENCIES) + '% of the defined libraries '
                             'in the config file(s) are strictly (==) defined. We found '
                           + str(nbr_imports_in_config)
                           + ' libraries in the config file(s). From these '
                           + str(pct_strict_declarations_in_config)
                           + '% were strictly specified.\n')

    # config file present but no relevant source code imports
    if (nbr_config_files > 0) and (nbr_imports_in_sc <= 0):
        # doesnt matter whats inside the config file
        mentioned_to_all_used_val = 1 * SC_IMP_IN_CONF_WEIGHT

        se_feedback.append('1. Libraries used in the source-code and mentioned in config file scoring '
                           '(score: '
                           + str(mentioned_to_all_used_val)
                           + ' out of ' + str(SC_IMP_IN_CONF_WEIGHT) + '): We found that '
                                                                       'no relevant imports are used in the source '
                                                                       'code so there is no need to define any imports '
                                                                       'in a configuration file.\n')

        # if declarations have been made they should be strict
        pct_strict_declarations_in_config = analysis_result[31]
        strict_declarations_in_config_val = round(range_normalization(pct_strict_declarations_in_config,
                                                                      MIN_D_STRICT_DEPENDENCIES,
                                                                      MAX_D_STRICT_DEPENDENCIES,
                                                                      0, 1) * STRICT_DEPENDENCIES_WEIGHT, 2)

        se_feedback.append('2. Strictly defined libraries in config file(s) scoring (score: '
                           + str(strict_declarations_in_config_val)
                           + ' out of ' + str(STRICT_DEPENDENCIES_WEIGHT) + '): We expect that '
                           + str(MAX_D_STRICT_DEPENDENCIES) + '% of the defined libraries '
                             'in the config file(s) are strictly (==) defined. We found '
                           + str(nbr_imports_in_config)
                           + ' libraries in the config file(s). From these '
                           + str(pct_strict_declarations_in_config)
                           + '% were strictly specified.\n')

    # no config file present but relevant source code imports
    if (nbr_config_files <= 0) and (nbr_imports_in_sc > 0):
        # both values are 0
        mentioned_to_all_used_val = 0
        strict_declarations_in_config_val = 0

        se_feedback.append('> Config file(s) scoring (score: 0 out of ' +
                           str((STRICT_DEPENDENCIES_WEIGHT + SC_IMP_IN_CONF_WEIGHT)) + '): No Config file(s) detected '
                                                                                       'but we found '
                           + str(nbr_imports_in_sc) + ' relevant source code imports which should be included in an '
                                                      'configuration file. '
                                                      'You should add one (e.g. requirements.txt, config.env, '
                                                      'config.yaml, Dockerfile) in '
                                                      'order for others to reproduce your repository with the same '
                                                      'software '
                                                      'environment. We expect from a good config file to strictly '
                                                      'specify all library '
                                                      'versions and to cover all of the relevant libraries used in '
                                                      'the source code. '
                                                      'Relevant libraries are ones not included in the Python Standard '
                                                      'Library (see: '
                                                      'https://docs.python.org/3/library/) or local Python modules.\n')

    # no config file present but also no relevant source code imports
    if (nbr_config_files <= 0) and (nbr_imports_in_sc <= 0):
        # both values are max
        mentioned_to_all_used_val = 1 * SC_IMP_IN_CONF_WEIGHT
        strict_declarations_in_config_val = 1 * STRICT_DEPENDENCIES_WEIGHT

        se_feedback.append('> Config file(s) scoring (score: '
                           + str((STRICT_DEPENDENCIES_WEIGHT + SC_IMP_IN_CONF_WEIGHT))
                           + ' out of ' + str((STRICT_DEPENDENCIES_WEIGHT + SC_IMP_IN_CONF_WEIGHT))
                           + '): No Config file(s) detected but we also '
                             'didnt find any relevant source code imports which should be included in an '
                             'configuration file. If you include a not local Python module or one that is not included '
                             'in the Python Standard Library (see: https://docs.python.org/3/library/) please create a '
                             'configuration file (e.g. requirements.txt, config.env, config.yaml, Dockerfile) in '
                             'order for others to reproduce your repository with the same software environment. '
                             'We expect from a good config file to strictly specify all library '
                             'versions and to cover all of the relevant libraries used in the source code. \n')

    # if relevant source code imports occurred check how many of them are publicly available
    if nbr_imports_in_sc > 0:
        pct_public_source_code_imports = analysis_result[26]
        public_source_code_imports_val = range_normalization(pct_public_source_code_imports,
                                                             MIN_D_PUB_ACC_LIBS_IN_SC, MAX_D_PUB_ACC_LIBS_IN_SC,
                                                             0, 1) * PUB_ACC_LIBS_IN_SC_WEIGHT

        se_feedback.append('- Public available libraries in source code file(s) scoring (score: '
                           + str(public_source_code_imports_val)
                           + ' out of ' + str(PUB_ACC_LIBS_IN_SC_WEIGHT) + ': We expect all of the not local modules '
                             'or standard python libraries to be publicly available. We found that '
                           + str(pct_public_source_code_imports)
                           + '% are publicly available. We tested if the used library imports are accessible on '
                             'https://pypi.org. If the score is not ' + str(PUB_ACC_LIBS_IN_SC_WEIGHT) + ' (=100%): '
                             'Please try avoiding the use of '
                             'not public libraries as third parties may not be able to use your repository. Please '
                             'note: It is also possible that, if the score is not the maxima, all libraries are '
                             'publicly '
                             'available, but we could not find a match. If you are unsure please recheck manually.\n')

    # no relevant imports in source code -> all of them are available
    else:
        public_source_code_imports_val = 1 * PUB_ACC_LIBS_IN_SC_WEIGHT

        se_feedback.append('- Public available libraries in source code file(s) scoring (score: '
                           + str(PUB_ACC_LIBS_IN_SC_WEIGHT)
                           + ' out of ' + str(PUB_ACC_LIBS_IN_SC_WEIGHT) + ': We expect all of the not local modules '
                             'or standard python libraries to be publicly available. We found no relevant source code '
                             'imports, so 100% are publicly available. We would have tested if the used library '
                             'imports are accessible on https://pypi.org.\n')

    # build overall result
    se_feedback.append('> Software environment is calculated from the above identifiers. '
                       'Since these have a different influence on the overall result, they are weighted as '
                       'follows:\n'
                       + '- Source-code imports in config file weight: '
                       + str(SC_IMP_IN_CONF_WEIGHT) + '\n'
                       + '- Strict dependency declarations in config file weight: '
                       + str(STRICT_DEPENDENCIES_WEIGHT) + '\n'
                       + '- Public libs in source code weight: '
                       + str(PUB_ACC_LIBS_IN_SC_WEIGHT) + '\n'
                       + '\n'
                       + '> Important note: For our analysis we exclude python standard libraries (see: '
                         'https://docs.python.org/3/library/) as '
                         'well as local file imports. We also eliminate duplicates (if one import '
                         'occurs in multiple files we count it as one).')

    software_env_value = round(mentioned_to_all_used_val + strict_declarations_in_config_val +
                               public_source_code_imports_val, 2)

    return software_env_value


# proof of concept: preprocessing functionality is missing
def dataset_availability_preprocessing_feedback(analysis_result):
    # dataset file candidates mentioned in source code
    ds_file_candidates_mentioned_in_sc = analysis_result[37]
    # dataset reference in README file(s)
    ds_readme_reference = analysis_result[8]

    if (ds_file_candidates_mentioned_in_sc > 0) or (ds_readme_reference == 1):
        dataset_val = 1

        if ds_file_candidates_mentioned_in_sc > 0:
            ds_feedback.append('Dataset availability and preprocessing scoring (score: 1.0 out of 1.0): '
                               'Dataset file candidate(s) were mentioned in the source code. '
                               'This is best practice, because one should always provide a dataset (if possible) in '
                               'the repository '
                               'in order for others to reproduce your repository with the same input data.\n')
        else:
            ds_feedback.append('Dataset availability and preprocessing scoring (score: 1.0 out of 1.0): '
                               'Dataset reference was found in the README. '
                               'This is not best practice, because one should always provide a dataset (if possible) '
                               'locally in the repository '
                               'in order for others to reproduce your repository with the same input data. Of course '
                               'this is not always possible, especially when dealing with larger datasets.\n')
    else:
        dataset_val = 0
        ds_feedback.append('Dataset availability and preprocessing scoring (score: 0 out of 1.0): '
                           'No dataset file candidate(s) are mentioned in the source code or referenced within the '
                           'README. '
                           'If you have provided a dataset in your repository '
                           'move it in a folder named "data" or rename the dataset with "data" in name.'
                           ' You should always provide a dataset (if possible) in the repository '
                           'in order for others to reproduce your repository with the same input data. '
                           'Linking the dataset in the README is an option, but it can not be guaranteed that the '
                           'dataset will be '
                           'accessible in the future so this (usually) not the best solution (except if you deal with '
                           'large datasets). If you have linked the dataset in the '
                           'README but the tool has not detected it, move it into an separate section with "data" '
                           'in the name and provide the name of the dataset as well as the link to it.\n')

    ds_feedback.append('> Dataset preprocessing detection is currently not implemented. But: If you preprocessed the '
                       'dataset in any way please make sure to include either the final dataset or files to reproduce '
                       'the steps taken.')

    return dataset_val


def random_seed_feedback(analysis_result):
    # how many declaration lines of random seed found
    nbr_rdm_seed_lines = analysis_result[22]
    # how many random seed lines of the found are fixing the seed
    pct_fixed_rdm_seed_lines = analysis_result[23]

    # if no random seed in code -> perfectly fine (no randomness)
    if nbr_rdm_seed_lines > 0:
        # no weight needed because this is the only value (not important how many there are just how many of them fix)
        pct_fixed_rdm_seed_lines_val = range_normalization(pct_fixed_rdm_seed_lines, 0, 100, 0, 1)
        random_seed_val = round(pct_fixed_rdm_seed_lines_val, 2)

        rs_feedback.append('Random seed lines with fixed seed scoring (score: '
                           + str(random_seed_val)
                           + ' out of 1.0): We found that '
                           + str(pct_fixed_rdm_seed_lines)
                           + '% of the '
                           + str(nbr_rdm_seed_lines)
                           + ' found random seed declaration lines had a fixed seed. If the value is not 100% make '
                             'sure to fix the random seeds.')
    else:
        random_seed_val = 0

        rs_feedback.append('Random seed scoring (score: 0.0 out of 1.0): '
                           'No random seed declaration(s) found in the source-code. This results in the worst score, '
                           'as we assume that the random number generator has different starting points each time.'
                           'If you have declared a random seed but we were not able to detect it, make sure to fix the '
                           'value of it in order for others to use the same seed.'
                           'If you have not declared a seed please do so, and assign a specific value to it.')

    return random_seed_val


def model_serialization_feedback(analysis_result):
    ms_used = analysis_result[24]

    if ms_used == 'Yes':
        ms_val = 1
        ms_feedback.append('Model serialization scoring (score: 1.0 out of 1.0): '
                           'Model serialization artifacts found. Model serialization helps in the field of machine '
                           'learning, where incremental improvements should be documented in order for others to '
                           'understand the steps taken. We look for one of the following: a) folders named ".dvc", b) '
                           'files with the extensions ".dvc", ".h5", ".pkl" or ".model" '
                           'c) one of the following keywords in the source code: "torch.save()", "pickle.dump" or '
                           '"joblib".')

    else:
        ms_val = 0
        ms_feedback.append('Model serialization scoring (score: 0 out of 1.0): '
                           'No model serialization artifacts found. '
                           'Model serialization helps in the field of machine learning, where incremental improvements '
                           'should be documented in order for others to understand the steps taken. '
                           'We look for one of the following: a) folders named ".dvc", b) '
                           'files with the extensions ".dvc", ".h5", ".pkl" or ".model" '
                           'c) one of the following keywords in the source code: "torch.save()", "pickle.dump" or '
                           '"joblib".')

    return ms_val


def hyperparameter_feedback(analysis_result):
    # only really important if no model serialization -> because if model serialised: all hp's documented anyways
    nbr_hp_indicators = analysis_result[25]

    if nbr_hp_indicators > 0:
        hp_val = 1
        hp_feedback.append('Hyperparameter logging scoring (score: 1.0 out of 1.0): We found '
                           + str(nbr_hp_indicators)
                           + ' hyperparameter logging indicator(s) in the source code. '
                             ' Logging changes of the hyper-parameters helps in the field of machine learning, '
                             'where incremental improvements should be documented in order for others to understand '
                             'the steps taken.')
    else:
        hp_val = 0
        hp_feedback.append('Hyperparameter logging scoring (score: 0 out of 1.0): '
                           'No hyperparameter logging indicators found. We look out for imports of the following '
                           'libraries in the source code: "wandb", "neptune", "mlflow" and "sacred". These libraries '
                           'enable the logging of these parameters in order to document them. Also, we are looking '
                           'for method calls of these libraries regarding logging. '
                           'Logging changes of the hyper-parameters helps in the field of machine learning, '
                           'where incremental improvements should be documented in order for others to understand '
                           'the steps taken.')

    return hp_val


def out_of_the_box_buildability_feedback(analysis_result):
    ootb_buildable = analysis_result[39]

    if ootb_buildable == 'BinderHub not reachable':
        binderhub_val = 0
        bh_feedback.append('Out-of-the-box buildability scoring (score: 0 out of 1.0): '
                           'Tested building the repository with BinderHub was not successful because the provided '
                           'BinderHub URL was not reachable. If you have no access to your own BinderHub deployment '
                           'you can use the free and publicly available infrastructure accessible under '
                           'https://www.mybinder.org to test. Please try if it builds successfully, as it greatly '
                           'helps reproducing the found results. If you have included a Dockerfile in your repository '
                           'it may not be compatible with BinderHub. '
                           'Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html')
    # if repo build with BinderHub successful
    elif ootb_buildable == 'Yes':
        binderhub_val = 1
        bh_feedback.append('Out-of-the-box buildability scoring (score: 1.0 out of 1.0): '
                           'Tested building the repository with BinderHub was successful. This greatly helps '
                           'reproducing the found results. You can use the free and publicly available infrastructure '
                           'accessible under https://www.mybinder.org to generate a Binder Badge which you should '
                           'include in the README.')
    else:
        binderhub_val = 0
        bh_feedback.append('Out-of-the-box buildability scoring (score: 0 out of 1.0): '
                           'Tested building the repository with BinderHub resulted in an error. Repository is not '
                           'buildable with BinderHub. Please try fixing this, as it greatly helps reproducing the '
                           'found results. You can use the free and publicly available infrastructure accessible under '
                           'https://www.mybinder.org to test. If you have included a Dockerfile in your repository '
                           'it may not be compatible with BinderHub. '
                           'Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html')

    return binderhub_val


def range_normalization(input_value, min_value, max_value, min_range, max_range):
    if input_value < min_value:
        input_value = min_value

    if input_value > max_value:
        input_value = max_value

    normalized_value = (((input_value - min_value) * (max_range - min_range)) / (
            max_value - min_value)) + min_range

    return normalized_value


def build_factor_context(sc_val, se_val, ds_val, rs_val, ms_val, hp_val, bh_val):
    # context for source-code availability and documentation factor
    if sc_val >= TOP_SCAD_THLD:
        sc_context = 'Score higher than top threshold (T). Very good.'
    elif sc_val > AVG_SCAD_THLD:
        sc_context = 'Score higher than average threshold (A). Seems good. Some improvements recommended.'
    # can be equal to MID
    elif sc_val > LOW_SCAD_THLD:
        sc_context = 'Score higher than lower threshold (L). Improvements should be made.'
    # must be equal or less than NEG
    else:
        sc_context = 'Score lower than lower threshold (L). Major improvements should be made.'

    factor_result.append('Source-code availability and documentation: ' + str(sc_val) + ' : ' + sc_context + ' : '
                         + str(TOP_SCAD_THLD) + ' : ' + str(AVG_SCAD_THLD) + ' : ' + str(LOW_SCAD_THLD))
    factor_context.append(sc_context)

    # context for software environment factor
    if se_val >= TOP_SE_THLD:
        se_context = 'Score higher than top threshold (T). Very good.'
    elif se_val > AVG_SE_THLD:
        se_context = 'Score higher than average threshold (A). Seems good. Some improvements recommended.'
    # can be equal to MID
    elif se_val > LOW_SE_THLD:
        se_context = 'Score higher than lower threshold (L). Improvements should be made.'
    # must be equal or less than NEG
    else:
        se_context = 'Score lower than lower threshold (L). Major improvements should be made.'

    factor_result.append('Software environment: ' + str(se_val) + ' : ' + se_context + ' : '
                         + str(TOP_SE_THLD) + ' : ' + str(AVG_SE_THLD) + ' : ' + str(LOW_SE_THLD))
    factor_context.append(se_context)

    # dataset availability and preprocessing context
    if ds_val == 1:
        ds_context = 'Score equal to top threshold (T). Very good.'
    else:
        ds_context = 'Score equal to lower threshold (L). Major improvements should be made.'

    factor_result.append('Dataset availability and preprocessing: ' + str(ds_val) + ' : ' + ds_context + ' : '
                         + str(1) + ' : ' + '-' + ' : ' + str(0))

    # random seed control context
    if rs_val >= TOP_RS_THLD:
        rs_context = 'Score higher than top threshold (T). Very good.'
    elif rs_val > AVG_RS_THLD:
        rs_context = 'Score higher than average threshold (A). Seems good. Some improvements recommended.'
    # can be equal to MID
    elif rs_val > LOW_RS_THLD:
        rs_context = 'Score higher than lower threshold (L). Improvements should be made.'
    # must be equal or less than NEG
    else:
        rs_context = 'Score lower than lower threshold (L). Major improvements should be made.'

    factor_result.append('Random seed control: ' + str(rs_val) + ' : ' + rs_context + ' : '
                         + str(TOP_RS_THLD) + ' : ' + str(AVG_RS_THLD) + ' : ' + str(LOW_RS_THLD))

    # model serialization context
    if ms_val == 1:
        ms_context = 'Score equal to top threshold (T). Very good.'
    else:
        ms_context = 'Score equal to lower threshold (L). Major improvements should be made.'

    factor_result.append('Model serialization: ' + str(ms_val) + ' : ' + ms_context + ' : '
                         + str(1) + ' : ' + '-' + ' : ' + str(0))

    # hyperparameter logging context
    if hp_val == 1:
        hp_context = 'Score equal to top threshold (T). Very good.'
    else:
        hp_context = 'Score equal to lower threshold (L). Major improvements should be made.'

    factor_result.append('Hyperparameter logging: ' + str(hp_val) + ' : ' + hp_context + ' : '
                         + str(1) + ' : ' + '-' + ' : ' + str(0))

    # out-of-the-box buildability context
    if bh_val == 1:
        bh_context = 'Score equal to top threshold (T). Very good.'
    else:
        bh_context = 'Score equal to lower threshold (L). Major improvements should be made.'

    factor_result.append('Out-of-the-box buildability: ' + str(bh_val) + ' : ' + bh_context + ' : '
                         + str(1) + ' : ' + '-' + ' : ' + str(0))

    # TODO: at the end append a line with * explaining where the threshold values are from
    factor_context.append(rs_context)


def build_feedback_file(file_path):
    feedback_txt = open(file_path, "w")
    feedback_txt.write('# REPRODUCIBILITY FACTOR SCORING (from 0 to 1): \n\n')
    table = '| Reproducibility factor | Score | Feedback | T* | A* | L* |\n| ----------- | ----------- | ----------- ' \
            '| ----------- | ----------- | ----------- |\n'
    for element in factor_result:
        elements = element.split(':')
        table = table + '| ' + str(elements[0]) + ' | ' + str(elements[1]) + ' | ' + str(elements[2]) + ' | ' \
                + str(elements[3]) + ' | ' + str(elements[4]) + ' | ' + str(elements[5]) + ' |\n'
    feedback_txt.write(table)
    thld_note = '\n> *: Thresholds computed from respective reproducible and non-reproducible sets of repositories. ' \
                'More information on this in the associated thesis in chapter 6.'
    feedback_txt.write(thld_note)
    feedback_txt.write('\n\n## SOURCE CODE AVAILABILITY AND DOCUMENTATION FEEDBACK\n\n')
    for element in sc_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## SOFTWARE ENVIRONMENT FEEDBACK\n\n')
    for element in se_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## DATASET AVAILABILITY AND PREPROCESSING FEEDBACK\n\n')
    for element in ds_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## RANDOM SEED FEEDBACK\n\n')
    for element in rs_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## MODEL SERIALIZATION FEEDBACK\n\n')
    for element in ms_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## HYPERPARAMETER LOGGING FEEDBACK\n\n')
    for element in hp_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\n## OUT-OF-THE-BOX BUILDABILITY FEEDBACK\n\n')
    for element in bh_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.close()

    print('\nWrote feedback to ' + file_path + '\n')


def print_reproducibility_factor_feedback(sc_availability_documentation_val, software_env_val,
                                          dataset_availability_preprocessing_val, random_seed_val,
                                          model_serialization_val, hyperparameter_val, ootb_buildability_val):
    console = Console()

    print('\n\n')
    print('[bold magenta] ____________________________________[/bold magenta]')
    print('[bold magenta]|   REPRODUCIBILITY FACTOR SCORING    |[/bold magenta]')
    print('[bold magenta]|____________________________________|[/bold magenta]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("reproducibility factor", justify="left")
    table.add_column("score (from 0 to 1)", justify="center")
    table.add_row('Source-code availability & documentation', str(sc_availability_documentation_val))
    table.add_row('Software environment', str(software_env_val))
    table.add_row('Dataset availability & preprocessing', str(dataset_availability_preprocessing_val))
    table.add_row('Random seed', str(random_seed_val))
    table.add_row('Model serialization', str(model_serialization_val))
    table.add_row('Hyperparameter logging', str(hyperparameter_val))
    table.add_row('Out of the box buildable with BinderHub', str(ootb_buildability_val))
    console.print(table)
    print('\n')

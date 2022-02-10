#!/usr/bin/python3

# builds cli + .txt feedback based on the retrieved result
from rich import print
from rich.console import Console
from rich.table import Table

import result_builder

# TODO: doc
# TODO: SAVE IN REPORT

factor_result = []
sc_feedback = []
se_feedback = []
ds_feedback = []
rs_feedback = []
ms_feedback = []
hp_feedback = []
bh_feedback = []

# BASELINES FOR PROPERTIES WHERE THE VALUE IS RELEVANT
# For the others the existence is enough e.g. open-source-license or not
BL_AVG_README_LINES = 50
BL_AVG_README_LINKS = 5
# not needed as it should be 100%? BL_PCT_ACC_README_LINKS = 0
BL_CODE_COMMENT_RATIO = 10
# not needed as it should be 10 (best)? BL_AVG_PYLINT_SCORE = 0
BL_PCT_SPEC_CONFIG_IMP = 0
BL_PCT_DETECTED_DATASET_CAND_IN_SC = 0
# not needed as percentage should always be 100%? BL_PCT_FXD_RDM_SEED_LINES = 0
BL_NMB_HP_IND = 1


# TODO: determine baseline values
def build_feedback(feedback_file_path):
    analysis_result = result_builder.get_analysis_result()

    sc_val = source_code_availability_documentation_feedback(analysis_result)
    se_val = software_environment_feedback(analysis_result)
    ds_val = dataset_availability_preprocessing_feedback(analysis_result)
    rs_val = random_seed_feedback(analysis_result)
    ms_val = model_serialization_feedback(analysis_result)
    hp_val = hyperparameter_feedback(analysis_result)
    bh_val = out_of_the_box_buildability_feedback(analysis_result)

    build_feedback_file(feedback_file_path)

    print_reproducibility_factor_feedback(sc_val, se_val, ds_val, rs_val, ms_val, hp_val, bh_val)


def source_code_availability_documentation_feedback(analysis_result):
    # first we define the weights of all indicators
    # change if you want to make the indicator more/less impactful
    total_license_weight = 1
    total_readme_weight = 1
    avg_readme_length_weight = 2
    avg_readme_links_weight = 0.5
    pct_acc_links_weight = 0.5
    avg_pylint_score_weight = 0.5
    code_comment_ratio_weight = 1

    # processing license
    nbr_licenses = analysis_result[8]
    # ranging from 0 to nbr_licenses
    nbr_os_licenses = analysis_result[9]
    license_value = calculate_license_value(nbr_licenses, nbr_os_licenses)
    weighted_license_value = license_value * total_license_weight

    # processing readme
    readme_value = calculate_readme_value(analysis_result, avg_readme_length_weight, avg_readme_links_weight,
                                          pct_acc_links_weight)
    weighted_readme_value = readme_value * total_readme_weight

    # processing pylint scoring
    # should be more generalised for other source code types
    # TODO: user feedback on how to improve (if necessary)
    avg_pylint_score = analysis_result[17]
    pylint_value = range_normalization(avg_pylint_score, -10, 10, 0, 1)

    sc_feedback.append('\t3. Source-code pylint rating (score: '
                       + str(round(pylint_value, 2))
                       + ' out of 1.0): Not normalized pylint rating is '
                       + str(round(avg_pylint_score, 2))
                       + ' where 10.0 is best. We found that readable code is best for reproducibility.\n')

    weighted_pylint_value = pylint_value * avg_pylint_score_weight

    # processing code comment ratio
    # for code comment ratio: > BL bad but < BL also bad should be value approx = BL
    # TODO: user feedback on how to improve (if necessary)
    code_comment_ratio = analysis_result[16]
    # 1 - method result because of if code comment ratio < BL_CODE_COMMENT_RATIO it's good
    # less code lines per comment line (usually) means better explanation
    code_comment_ratio_value = (1 - range_normalization(code_comment_ratio, BL_CODE_COMMENT_RATIO,
                                                        5 * BL_CODE_COMMENT_RATIO, 0, 1))
    weighted_code_comment_ratio_value = code_comment_ratio_value * code_comment_ratio_weight

    sc_feedback.append('\t4. Source-code-comment-ratio rating (score: '
                       + str(round(code_comment_ratio_value, 2))
                       + ' out of 1.0): We determined '
                       + str(BL_CODE_COMMENT_RATIO)
                       + ' as best ratio. But more comments are good too. Well documented code is important.\n')

    # as all values are ranging from 0 to 1 the max value for each entry is 1 * corresponding weight
    max_value = total_readme_weight + total_license_weight + avg_pylint_score_weight + code_comment_ratio_weight
    actual_value = weighted_license_value + weighted_readme_value + weighted_pylint_value \
                   + weighted_code_comment_ratio_value

    sc_feedback.append('\tSource-code availability and documentation is calculated from the above identifiers. '
                       'Since these have a different influence on the overall result, they are weighted as follows:\n\n'
                       + '\tLicense weight: ' + str(total_license_weight) + '\n'
                       + '\tSub-readme: Length weight: ' + str(avg_readme_length_weight) + '\n'
                       + '\tSub-readme: # links weight: ' + str(avg_readme_links_weight) + '\n'
                       + '\tSub-readme: % accessible links weight: ' + str(pct_acc_links_weight) + '\n'
                       + '\tReadme weight: ' + str(total_readme_weight) + '\n'
                       + '\tPylint weight: ' + str(avg_pylint_score_weight) + '\n'
                       + '\tCode-comment-ratio weight: ' + str(code_comment_ratio_weight))

    sc_availability_documentation_value = round(range_normalization(actual_value, 0, max_value, 0, 1), 2)
    factor_result.append('\tSource-code availability and documentation: ' + str(sc_availability_documentation_value))
    return sc_availability_documentation_value


def calculate_license_value(nbr_licenses, nbr_os_licenses):
    normalized_license_value = range_normalization(nbr_os_licenses, 0, nbr_licenses, 0, 1)

    if nbr_licenses == 0:
        sc_feedback.append('\t1. License rating (score: '
                           + str(round(normalized_license_value, 2))
                           + ' out of 1.0): No license information found. Providing a licenses helps others to tell if '
                             'your project and its dependencies are available to them.\n')
    elif nbr_os_licenses == 0:
        sc_feedback.append('\t1. License rating (score: '
                           + str(round(normalized_license_value, 2))
                           + ' out of 1.0): All found licenses are not open-source. Using open-source dependencies '
                             'enables others to use them also.\n')
    elif nbr_licenses != nbr_os_licenses:
        sc_feedback.append('\t1. License rating (score: '
                           + str(round(normalized_license_value, 2))
                           + ' out of 1.0): '
                           + str((nbr_licenses - nbr_os_licenses))
                           + ' of the '
                           + str(nbr_licenses)
                           + ' found licenses are not open-source. Using open-source dependencies enables others to '
                             'use them also.\n')
    else:
        sc_feedback.append('\t1. License rating (score: '
                           + str(round(normalized_license_value, 2))
                           + ' out of 1.0): All found licenses are open-source.\n')

    return normalized_license_value


def calculate_readme_value(analysis_result, avg_length_weight, avg_links_weight,
                           pct_acc_links_weight):
    # TODO: user feedback on how to improve (if necessary)
    nbr_readmes = analysis_result[1]

    if nbr_readmes > 0:
        avg_readme_length = analysis_result[3]
        avg_readme_length_value = range_normalization(avg_readme_length, 0, BL_AVG_README_LINES, 0,
                                                      1) * avg_length_weight

        sc_feedback.append('\tSub-value for ReadMe: Average length rating (score: '
                           + str(round(avg_readme_length_value / avg_length_weight, 2))
                           + ' out of 1.0): We determined that '
                           + str(BL_AVG_README_LINES)
                           + ' or more lines are best. We found '
                           + str(avg_readme_length)
                           + ' lines (in average) in the ReadMe file(s)')

        avg_readme_links = analysis_result[4] / nbr_readmes
        avg_readme_links_value = range_normalization(avg_readme_links, 0, BL_AVG_README_LINKS, 0, 1) * avg_links_weight

        sc_feedback.append('\tSub-value for ReadMe: Average links rating (score: '
                           + str(round(avg_readme_links_value / avg_links_weight, 2))
                           + ' out of 1.0): We determined that '
                           + str(BL_AVG_README_LINKS)
                           + ' or more links are best. We found '
                           + str(avg_readme_links)
                           + ' links (in average) in the ReadMe file(s)')

        if avg_readme_links > 0:
            pct_not_acc_links = analysis_result[7]
            pct_acc_links = 100 - pct_not_acc_links
            pct_acc_links_value = range_normalization(pct_acc_links, 0, 100, 0, 1) * pct_acc_links_weight

            sc_feedback.append('\tSub-value for ReadMe: % of links accessible rating (score: '
                               + str(round(pct_acc_links_value / pct_acc_links_weight, 2))
                               + ' out of 1.0): We expect 100% of them to be accessible. We found '
                               + str(pct_acc_links)
                               + '% accessible links in the ReadMe file(s).')
        else:
            pct_acc_links_value = 0

        # as all values are ranging from 0 to 1 the max value for each entry is 1 * corresponding weight
        max_readme_value = avg_length_weight + avg_links_weight + pct_acc_links_weight

        all_readme_values = avg_readme_length_value + avg_readme_links_value \
                            + pct_acc_links_value

        normalized_readme_value = range_normalization(all_readme_values, 0, max_readme_value, 0, 1)

        sc_feedback.append('\n\t2. ReadMe overall rating (score: '
                           + str(round(normalized_readme_value, 2))
                           + ' out of 1.0): See sub-ratings for more information.\n')
        return normalized_readme_value
    # if no readme
    else:
        sc_feedback.append('\t2. ReadMe rating (score: 0 out of 1.0): No ReadMe file(s) found. '
                           'You should add one to document your repository. We expect from a good ReadMe to have '
                           + str(BL_AVG_README_LINES)
                           + ' lines. Make sure to also add useful links e.g. a paper link. We determined that '
                           + str(BL_AVG_README_LINKS)
                           + ' or more links are best. Make also sure that all provided links are correct and '
                             'reachable. Also add a binder badge if possible (see out-of-the-box buildability '
                             'feedback.)\n')
        return 0


def software_environment_feedback(analysis_result):
    nbr_config_imports_weight = 1
    pct_strict_config_imports_weight = 1
    pct_mentioned_to_all_used_weight = 1

    nbr_config_files = analysis_result[25]
    # TODO: replace this value with baseline (how many imports in config are normal for reproducible repos)
    nbr_imports_in_sc = analysis_result[28]

    # TODO: user feedback on how to improve (if necessary)
    if nbr_config_files > 0:
        # how many imports in config
        nbr_imports_in_config = analysis_result[27]
        # how many of those are strict specified (==)
        pct_strict_imports_in_config = analysis_result[29]
        # how many of the used imports in source code are mentioned in config
        pct_mentioned_to_all_used = analysis_result[31]
        if nbr_imports_in_sc == 0:
            nbr_imports_in_config_val = 1
            pct_mentioned_to_all_used_val = 1
            pct_strict_imports_in_config_val = 1

            se_feedback.append('\tWe found no library imports in the source code. Therefore the rating of the config '
                               'file will be 1.0 out of 1.0 no matter what is inside as none of the defined libraries '
                               'are used.')

        else:
            # relation: all defined config libs in relation to all soure-code libs
            nbr_imports_in_config_val = range_normalization(nbr_imports_in_config, 0, nbr_imports_in_sc, 0, 1) \
                                        * nbr_config_imports_weight

            se_feedback.append('\t1. Number of libraries in config file(s) rating (score: '
                               + str(round(nbr_imports_in_config_val / nbr_config_imports_weight, 2))
                               + ' out of 1.0): We expect all of the in the source-code used libraries to be '
                                 'mentioned. We found '
                               + str(nbr_imports_in_config)
                               + ' libraries in the config file(s). We found '
                               + str(nbr_imports_in_sc)
                               + ' libraries in the source-code file(s).\n')

            # relation: all config libs used in the source code in relation to all source-code libs
            pct_mentioned_to_all_used_val = range_normalization(pct_mentioned_to_all_used, 0, 100, 0, 1) \
                                            * pct_mentioned_to_all_used_weight

            se_feedback.append('\n\t2. Percentage of libraries in config file(s) who are also used in the source-code '
                               'in relation to all used in the source-code file(s) rating (score: '
                               + str(round(pct_mentioned_to_all_used_val / pct_mentioned_to_all_used_weight, 2))
                               + ' out of 1.0): We found that '
                               + str(pct_mentioned_to_all_used)
                               + '% of the used libraries are defined in the config file(s). We expect that at least '
                                 'the in the source-code used libraries are all'
                                 ' defined in the config file(s). More are useless but not harmful.\n')

            pct_strict_imports_in_config_val = range_normalization(pct_strict_imports_in_config, 0, 100, 0, 1) \
                                                * pct_strict_config_imports_weight

            se_feedback.append('\n\t3. Percentage of strict defined libraries in config file(s) rating (score: '
                               + str(round(pct_strict_imports_in_config_val / pct_strict_config_imports_weight, 2))
                               + ' out of 1.0): We expect all of the defined libraries in the config file(s) to be '
                                 'strictly (==) defined. We found '
                               + str(nbr_imports_in_config)
                               + ' libraries in the config file(s). From these '
                               + str(pct_strict_imports_in_config)
                               + '% were strictly specified.\n')

        max_value = nbr_config_imports_weight + pct_strict_config_imports_weight + pct_mentioned_to_all_used_weight
        actual_value = nbr_imports_in_config_val + pct_strict_imports_in_config_val + pct_mentioned_to_all_used_val

        software_env_value = round(range_normalization(actual_value, 0, max_value, 0, 1), 2)

        se_feedback.append('\tSoftware environment is calculated from the above identifiers. '
                           'Since these have a different influence on the overall result, they are weighted as '
                           'follows:\n\n'
                           + '\tNumber of config imports weight: ' + str(nbr_config_imports_weight) + '\n'
                           + '\tStrict config imports weight: ' + str(pct_strict_config_imports_weight) + '\n'
                           + '\tImports in config in relation to all in source-code weight: '
                           + str(pct_mentioned_to_all_used_weight))

        factor_result.append('\tSoftware environment: ' + str(software_env_value))

        return software_env_value
    else:
        software_env_value = 0

        se_feedback.append('\tSoftware environment rating (score: 0 out of 1.0): No Config file(s) found. '
                           'You should add one (e.g. requirements.txt, config.env, config.yaml, Dockerfile) in order '
                           'for others to reproduce your repository with the same software '
                           'environment. We expect from a good config file to strictly specify all library versions '
                           'and to cover all of the used libraries used in the source code.)')

        factor_result.append('\tSoftware environment: ' + str(software_env_value))
        return software_env_value


# proof of concept: preprocessing functionality is missing
def dataset_availability_preprocessing_feedback(analysis_result):
    candidates_weight = 1
    mentioned_weight = 1
    pct_mentioned_found_weight = 1

    # dataset file candidates (if 0 -> 0 overall)
    dataset_file_candidates = analysis_result[34]
    if dataset_file_candidates == 0:
        ds_feedback.append('\tDataset availability and documentation rating (score: 0 out of 1.0): '
                           'No dataset file candidate(s) found. If you have provided a dataset in your repository '
                           'move it in a folder named "data" or rename the dataset with "data" in name.'
                           ' You should always provide a dataset (if possible) in the repository '
                           'in order for others to reproduce your repository with the same input data. '
                           'Linking the dataset would be an option, but as can not guarantee that the dataset will be '
                           'accessible in the future it is not a good solution.')
        return 0
    else:
        # TODO:BASELINE for how many candidates is good
        max_val_candidates = 1  # TODO: change should be baseline val
        max_val_mentioned = 1  # TODO: change should be baseline val
        dataset_file_candidates_val = range_normalization(dataset_file_candidates, 0, max_val_candidates, 0, 1) \
                                      * candidates_weight

        # TODO: edit message when baseline val is clear.
        ds_feedback.append('\t1. Dataset file candidates rating (score: '
                           + str(round(dataset_file_candidates_val / candidates_weight, 2))
                           + ' out of 1.0): We found '
                           + str(dataset_file_candidates)
                           + ' dataset file candidates in the repository.\n')

        # # dataset file candidates mentioned in source code
        ds_file_candidates_mentioned_in_sc = analysis_result[35]
        ds_file_candidates_mentioned_in_sc_val = range_normalization(ds_file_candidates_mentioned_in_sc,
                                                                     0, max_val_mentioned, 0, 1) * mentioned_weight

        # TODO: edit message when baseline val is clear.
        # how many dataset file candidates were mentioned in the source code
        ds_feedback.append('\n\t2. Dataset file candidates in source code rating (score: '
                           + str(round(ds_file_candidates_mentioned_in_sc_val / mentioned_weight, 2))
                           + ' out of 1.0): Of the '
                           + str(dataset_file_candidates)
                           + ' dataset file candidates we found in the repository, '
                           + str(ds_file_candidates_mentioned_in_sc)
                           + ' of them were the source-code.\n')

        # % mentioned in relation to all
        # of all found dataset file candidates how many of them were in the source-code
        pct_ds_candidates_mentioned_to_all_found = analysis_result[36]
        pct_ds_candidates_mentioned_to_all_found_val = range_normalization(pct_ds_candidates_mentioned_to_all_found,
                                                                           0, 100, 0, 1) * pct_mentioned_found_weight

        ds_feedback.append('\n\t3. Percentage of mentioned to all found dataset file candidates rating (score: '
                           + str(round(pct_ds_candidates_mentioned_to_all_found_val / pct_mentioned_found_weight, 2))
                           + ' out of 1.0): '
                           + str(pct_ds_candidates_mentioned_to_all_found)
                           + '% of the found dataset file candidates were mentioned in the source-code.\n')

        ds_feedback.append('\tImportant note: If you have provided a dataset in your repository but this tool has not '
                           'detected it, move it in a folder named "data" or rename the dataset with "data" in name.\n')

        ds_feedback.append('\tDataset availability and preprocessing is calculated from the above identifiers. '
                           'Since these have a different influence on the overall result, they are weighted as '
                           'follows:\n\n'
                           + '\tNumber of dataset file candidates weight: ' + str(candidates_weight) + '\n'
                           + '\tMentioned dataset file candidates in source-code weight: ' + str(mentioned_weight)
                           + '\n'
                           + '\tDataset file candidates found in source-code in relation to all found weight: '
                           + str(pct_mentioned_found_weight))

        max_value = candidates_weight + mentioned_weight + pct_mentioned_found_weight
        actual_value = dataset_file_candidates_val + ds_file_candidates_mentioned_in_sc_val \
                       + pct_ds_candidates_mentioned_to_all_found_val

        dataset_val = round(range_normalization(actual_value, 0, max_value, 0, 1), 2)
        factor_result.append('\tDataset availability and preprocessing: ' + str(dataset_val))

        return dataset_val


def random_seed_feedback(analysis_result):
    # how many declaration lines of random seed found
    nbr_rdm_seed_lines = analysis_result[21]
    # how many random seed lines of the found are fixing the seed
    pct_fixed_rdm_seed_lines = analysis_result[22]

    random_seed_val = 1
    # if no random seed in code -> perfectly fine (no randomness)
    if nbr_rdm_seed_lines > 0:
        # no weight needed because this is the only value (not important how many there are just how many of them fix)
        pct_fixed_rdm_seed_lines_val = range_normalization(pct_fixed_rdm_seed_lines, 0, 100, 0, 1)
        random_seed_val = round(pct_fixed_rdm_seed_lines_val, 2)

        rs_feedback.append('\tPercentage of random seed lines with fixed seed rating (score: '
                           + str(random_seed_val)
                           + ' out of 1.0): We found that '
                           + str(pct_fixed_rdm_seed_lines)
                           + '% of the '
                           + str(nbr_rdm_seed_lines)
                           + ' found random seed declaration lines had a fixed seed. If the value is not 100% make '
                             'sure to fix the random seeds.')
    else:
        rs_feedback.append('\tRandom seed rating (score: 1 out of 1.0): '
                           'No random seed declaration(s) found in the source-code. This results in the best score, '
                           'as we assume that no randomness regarding the test/train-split is involved in that case. '
                           'If you have declared a random seed but we were not able to detect it, make sure to fix the '
                           'value of it in order for others to use the same seed.')

    factor_result.append('\tRandom seed: ' + str(random_seed_val))
    return random_seed_val


def model_serialization_feedback(analysis_result):
    ms_used = analysis_result[23]
    ms_val = 0
    if ms_used == 'Yes':
        ms_val = 1
        ms_feedback.append('\tModel serialization rating (score: 1.0 out of 1.0): '
                           'Model serialization artefacts found. Model serialization helps in the field of machine '
                           'learning, where incremental improvements should be documented in order for others to '
                           'understand the steps taken.')
    else:
        ms_feedback.append('\tModel serialization rating (score: 0 out of 1.0): '
                           'No model serialization artefacts found. We look out for a .dvc folder in order to '
                           'determine whether or not model serialization has been used. If you have used it move the '
                           'corresponding artefacts in a .dvc folder. If you have not used it, consider doing so. '
                           'Model serialization helps in the field of machine learning, where incremental improvements '
                           'should be documented in order for others to understand the steps taken.')

    factor_result.append('\tModel serialization: ' + str(ms_val))
    return ms_val


def hyperparameter_feedback(analysis_result):
    # only really important if no model serialization -> because if model serialised: all hp's documented anyways
    nbr_hp_indicators = analysis_result[24]
    hp_val = 0

    if nbr_hp_indicators > 0:
        hp_val = round(range_normalization(nbr_hp_indicators, 0, BL_NMB_HP_IND, 0, 1), 2)

        hp_feedback.append('\tHyperparameter declaration rating (score: '
                           + str(hp_val)
                           + ' out of 1.0): We found '
                           + str(nbr_hp_indicators)
                           + ' hyperparameter declaration indicator(s) in the source code. '
                             'We determined that '
                           + str(BL_NMB_HP_IND)
                           + ' hyperparameter declaration indicators are a good value.'
                           ' Documenting changes of the hyperparameters helps in the field of machine learning, '
                           'where incremental improvements should be documented in order for others to understand '
                           'the steps taken.')
    else:
        hp_feedback.append('\tHyperparameter declaration rating (score: 0 out of 1.0): '
                           'No hyperparameter declarations found. We look out for imports of the following libraries '
                           'in the source code: "wandb", "neptune", "kubeflow" and "sacred". These libraries enable '
                           'the logging of these parameters in order to document them. '
                           'Documenting changes of the hyperparameters helps in the field of machine learning, '
                           'where incremental improvements should be documented in order for others to understand '
                           'the steps taken.')

    factor_result.append('\tHyperparameter declaration: ' + str(hp_val))
    return hp_val


def out_of_the_box_buildability_feedback(analysis_result):
    ootb_buildable = analysis_result[37]

    # TODO: user feedback on how to improve (if necessary)
    if ootb_buildable == 'BinderHub not reachable':
        binderhub_val = 0
        bh_feedback.append('\tOut-of-the-box buildability rating (score: 0 out of 1.0): '
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
        bh_feedback.append('\tOut-of-the-box buildability rating (score: 1.0 out of 1.0): '
                           'Tested building the repository with BinderHub was successful. This greatly helps '
                           'reproducing the found results. You can use the free and publicly available infrastructure '
                           'accessible under https://www.mybinder.org to generate a Binder Badge which you should '
                           'include in your ReadMe.')
    else:
        binderhub_val = 0
        bh_feedback.append('\tOut-of-the-box buildability rating (score: 0 out of 1.0): '
                           'Tested building the repository with BinderHub resulted in an error. Repository is not '
                           'buildable with BinderHub. Please try fixing this, as it greatly helps reproducing the '
                           'found results. You can use the free and publicly available infrastructure accessible under '
                           'https://www.mybinder.org to test. If you have included a Dockerfile in your repository '
                           'it may not be compatible with BinderHub. '
                           'Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html')

    factor_result.append('\tOut-of-the-box buildability: ' + str(binderhub_val))
    return binderhub_val


def range_normalization(input_value, min_value, max_value, min_range, max_range):
    if input_value < min_value:
        input_value = min_value

    if input_value > max_value:
        input_value = max_value

    normalized_value = (((input_value - min_value) * (max_range - min_range)) / (
            max_value - min_value)) + min_range

    return normalized_value


def build_feedback_file(file_path):
    feedback_txt = open(file_path, "w")
    feedback_txt.write('REPRODUCIBILITY FACTOR RATING (from 0 to 1): \n\n')
    for element in factor_result:
        feedback_txt.write(str(element) + "\n")
    feedback_txt.write('\n\nSOURCE CODE AVAILABILITY AND DOCUMENTATION FEEDBACK\n\n')
    for element in sc_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nSOFTWARE ENVIRONMENT FEEDBACK\n\n')
    for element in se_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nDATASET AVAILABILITY AND PREPROCESSING FEEDBACK\n\n')
    for element in ds_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nRANDOM SEED FEEDBACK\n\n')
    for element in rs_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nMODEL SERIALIZATION FEEDBACK\n\n')
    for element in ms_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nHYPERPARAMETER DECLARATION FEEDBACK\n\n')
    for element in hp_feedback:
        feedback_txt.write(element + "\n")
    feedback_txt.write('\n\nOUT-OF-THE-BOX BUILDABILITY FEEDBACK\n\n')
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
    print('[bold magenta]|   REPRODUCIBILITY FACTOR RATING    |[/bold magenta]')
    print('[bold magenta]|____________________________________|[/bold magenta]')

    table = Table(show_header=True, header_style="bold dim")
    table.add_column("reproducibility factor", justify="left")
    table.add_column("rating (from 0 to 1)", justify="center")
    table.add_row('Source-code availability & documentation', str(sc_availability_documentation_val))
    table.add_row('Software environment', str(software_env_val))
    table.add_row('Dataset availability & preprocessing', str(dataset_availability_preprocessing_val))
    table.add_row('Random seed', str(random_seed_val))
    table.add_row('Model serialization', str(model_serialization_val))
    table.add_row('Hyperparameter declaration', str(hyperparameter_val))
    table.add_row('Out of the box buildable with BinderHub', str(ootb_buildability_val))
    console.print(table)
    print('\n')

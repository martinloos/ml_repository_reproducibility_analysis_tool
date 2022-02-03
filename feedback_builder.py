#!/usr/bin/python3

# builds cli + .txt feedback based on the retrieved result

import result_builder

# TODO: doc
# TODO: implement

# BASELINES FOR PROPERTIES WHERE THE VALUE IS RELEVANT
# For the others the existence is enough e.g. open-source-license or not
BL_AVG_README_LINES = 0
BL_NBR_README_LINKS = 0
BL_PCT_NOT_ACC_README_LINKS = 0
BL_CODE_COMMENT_RATIO = 0
BL_AVG_PYLINT_SCORE = 0
BL_JN_W_HEADER = 0
BL_JN_W_FOOTER = 0
BL_PCT_FXD_RDM_SEED_LINES = 0
BL_NMB_HP_IND = 0
BL_PCT_SPEC_CONFIG_IMP = 0
BL_PCT_DETECTED_DATASET_CAND_IN_SC = 0


# TODO: determine baseline values
def build_feedback():
    analysis_result = result_builder.get_analysis_result()
    print('implement feedback')
    # source_code_availability_documentation_feedback()
    # software_environment_feedback()
    # out_of_the_box_buildability_feedback()
    # dataset_availability_preprocessing_feedback()
    # random_seed_feedback()
    # hyperparameter_feedback()
    # model_serialization_feedback()


def source_code_availability_documentation_feedback():
    print('feedback relating to this factor ')


def software_environment_feedback():
    print('feedback relating to this factor ')


def out_of_the_box_buildability_feedback():
    print('feedback relating to this factor ')


# proof of concept: preprocessing functionality is missing
def dataset_availability_preprocessing_feedback():
    print('feedback relating to this factor ')


def random_seed_feedback():
    print('feedback relating to this factor ')


def hyperparameter_feedback():
    print('feedback relating to this factor ')


def model_serialization_feedback():
    print('feedback relating to this factor ')

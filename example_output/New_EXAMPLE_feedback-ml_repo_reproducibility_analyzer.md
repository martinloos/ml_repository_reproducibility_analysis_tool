# REPRODUCIBILITY FACTOR RATING (from 0 to 1): 

| Reproducibility factor | Rating |
| ----------- | ----------- |
| Source-code availability and documentation |  0.95 |
| Software environment |  0.23 |
| Dataset availability and preprocessing |  0.69 |
| Random seed |  1.0 |
| Model serialization |  0 |
| Hyperparameter declaration |  0 |
| Out-of-the-box buildability |  0 |


## SOURCE CODE AVAILABILITY AND DOCUMENTATION FEEDBACK

1. License rating (score: 1.0 out of 1.0): All found licenses are open-source.

2. ReadMe overall rating (score: 1.0 out of 1.0): See sub-ratings for more information.

- Average length rating (score: 1.0 out of 1.0): We determined that 50 or more lines are best. We found 86.0 lines (in average) in the ReadMe file(s)
- Average links rating (score: 1.0 out of 1.0): We determined that 5 or more links are best. We found 12.0 links (in average) in the ReadMe file(s)
- % of links accessible rating (score: 1.0 out of 1.0): We expect 100% of them to be accessible. We found 100.0% accessible links in the ReadMe file(s).
3. Source-code pylint rating (score: 0.8 out of 1.0): Not normalized pylint rating is 6.09 where 10.0 is best. We found that readable code is best for reproducibility.

4. Source-code-comment-ratio rating (score: 0.93 out of 1.0): We determined 10 as best ratio. But more comments are good too. Well documented code is important.

> Source-code availability and documentation is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- License weight: 1
- Readme weight: 1
- Sub-readme: Length weight: 2
- Sub-readme: # links weight: 0.5
- Sub-readme: % accessible links weight: 0.5
- Pylint weight: 0.5
- Code-comment-ratio weight: 1


## SOFTWARE ENVIRONMENT FEEDBACK

1. Number of libraries in config file(s) rating (score: 0.34 out of 1.0): We expect all of the in the source-code used libraries to be mentioned. We found 10 libraries in the config file(s). We found 29 libraries in the source-code file(s).

2. Percentage of libraries in config file(s) who are also used in the source-code in relation to all used in the source-code file(s) rating (score: 0.24 out of 1.0): We found that 24.14% of the used libraries are defined in the config file(s). We expect that at least the in the source-code used libraries are all defined in the config file(s). More are useless but not harmful.

3. Percentage of strict defined libraries in config file(s) rating (score: 0.1 out of 1.0): We expect all of the defined libraries in the config file(s) to be strictly (==) defined. We found 10 libraries in the config file(s). From these 10.0% were strictly specified.

> Software environment is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- Number of config imports weight: 1
- Strict config imports weight: 1
- Imports in config in relation to all in source-code weight: 1


## DATASET AVAILABILITY AND PREPROCESSING FEEDBACK

1. Dataset file candidates rating (score: 1.0 out of 1.0): We found 14 dataset file candidates in the repository.

2. Dataset file candidates in source code rating (score: 1.0 out of 1.0): Of the 14 dataset file candidates we found in the repository, 1 of them were the source-code.

3. Percentage of mentioned to all found dataset file candidates rating (score: 0.07 out of 1.0): 7.14% of the found dataset file candidates were mentioned in the source-code.

> Important note: If you have provided a dataset in your repository but this tool has not detected it, move it in a folder named "data" or rename the dataset with "data" in name.

Dataset availability and preprocessing is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- Number of dataset file candidates weight: 1
- Mentioned dataset file candidates in source-code weight: 1
- Dataset file candidates found in source-code in relation to all found weight: 1


## RANDOM SEED FEEDBACK

Percentage of random seed lines with fixed seed rating (score: 1.0 out of 1.0): We found that 100.0% of the 5 found random seed declaration lines had a fixed seed. If the value is not 100% make sure to fix the random seeds.


## MODEL SERIALIZATION FEEDBACK

Model serialization rating (score: 0 out of 1.0): No model serialization artefacts found. We look out for a .dvc folder in order to determine whether or not model serialization has been used. If you have used it move the corresponding artefacts in a .dvc folder. If you have not used it, consider doing so. Model serialization helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken.


## HYPERPARAMETER DECLARATION FEEDBACK

Hyperparameter declaration rating (score: 0 out of 1.0): No hyperparameter declarations found. We look out for imports of the following libraries in the source code: "wandb", "neptune", "kubeflow" and "sacred". These libraries enable the logging of these parameters in order to document them. Documenting changes of the hyperparameters helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken.


## OUT-OF-THE-BOX BUILDABILITY FEEDBACK

Out-of-the-box buildability rating (score: 0 out of 1.0): Tested building the repository with BinderHub was not successful because the provided BinderHub URL was not reachable. If you have no access to your own BinderHub deployment you can use the free and publicly available infrastructure accessible under https://www.mybinder.org to test. Please try if it builds successfully, as it greatly helps reproducing the found results. If you have included a Dockerfile in your repository it may not be compatible with BinderHub. Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html

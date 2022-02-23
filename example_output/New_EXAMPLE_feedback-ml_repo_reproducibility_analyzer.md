# REPRODUCIBILITY FACTOR RATING (from 0 to 1): 

| Reproducibility factor | Rating |
| ----------- | ----------- |
| Source-code availability and documentation |  0.7 |
| Software environment |  0.54 |
| Dataset availability and preprocessing |  0.94 |
| Random seed |  0.72 |
| Model serialization |  1 |
| Hyperparameter declaration |  1.0 |
| Out-of-the-box buildability |  0 |


## SOURCE CODE AVAILABILITY AND DOCUMENTATION FEEDBACK

1. License rating (score: 1.0 out of 1.0): All found licenses are open-source.

2. ReadMe overall rating (score: 0.41 out of 1.0): See sub-ratings for more information.

- Average length rating (score: 0.26 out of 1.0): We determined that 50 or more lines are best. We found 13.2 lines (in average) in the ReadMe file(s)
- Average links rating (score: 0.7 out of 1.0): We determined that 5 or more links are best. We found 3.4 links (in average) in the ReadMe file(s)
- % of links accessible rating (score: 0.9 out of 1.0): We expect 100% of them to be accessible. We found 94.96% accessible links in the ReadMe file(s).
3. Source-code pylint rating (score: 0.7 out of 1.0): Not normalized pylint rating is 4.08 where 10.0 is best. We found that readable code is best for reproducibility.

4. Source-code-comment-ratio rating (score: 1.0 out of 1.0): We determined 10 as best ratio. But more comments are good too. Well documented code is important.

> Source-code availability and documentation is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- License weight: 0.1
- Readme weight: 0.4
- Sub-readme: Length weight: 0.7
- Sub-readme: # links weight: 0.2
- Sub-readme: % accessible links weight: 0.1
- Pylint weight: 0.2
- Code-comment-ratio weight: 0.3


## SOFTWARE ENVIRONMENT FEEDBACK

1. Number of libraries in config file(s) rating (score: 0.35 out of 1.0): We expect all of the in the source-code used libraries to be mentioned. We found 11 libraries in the config file(s). We found 30 libraries in the source-code file(s).

2. Percentage of libraries in config file(s) who are also used in the source-code in relation to all used in the source-code file(s) rating (score: 0.3 out of 1.0): We found that 30.0% of the used libraries are defined in the config file(s). We expect that at least the in the source-code used libraries are all defined in the config file(s). More are useless but not harmful.

3. Percentage of strict defined libraries in config file(s) rating (score: 0.8 out of 1.0): We expect all of the defined libraries in the config file(s) to be strictly (==) defined. We found 11 libraries in the config file(s). From these 81.82% were strictly specified.

- Percentage of public available libraries in source code file(s) rating (score: 0.97 out of 1.0): We expect all of the not local or standard python libraries to be publicly available. We found that 96.67% are publicly available. We tested if the used library imports are accessible on https://pypi.org. If the score is not 1.0 (=100%): Please try avoiding the use of not public libraries as third parties may not be able to use your repository. Please note: It is also possible that, if the score is not 1.0, all libraries are publicly available, but we could not find a match. If you are unsure please recheck manually.

> Software environment is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:
- Number of config imports weight: 0.2
- Strict config imports weight: 0.2
- Imports in config in relation to all in source-code weight: 0.4
- Percentage of public libs in source code weight: 0.2

> Important note: For our analysis we exclude python standard libraries (like os or sys) as well as local file imports. We also eliminate duplicates in the source code (if one import occurs in multiple files we count it as one).


## DATASET AVAILABILITY AND PREPROCESSING FEEDBACK

1. Dataset file candidates rating (score: 1.0 out of 1.0): We found 45 dataset file candidates in the repository.

2. Dataset file candidates in source code rating (score: 1.0 out of 1.0): Of the 45 dataset file candidates we found in the repository, 31 of them were the source-code.

3. Percentage of mentioned to all found dataset file candidates rating (score: 0.7 out of 1.0): 68.89% of the found dataset file candidates were mentioned in the source-code.

> Important note: If you have provided a dataset in your repository but this tool has not detected it, move it in a folder named "data" or rename the dataset with "data" in name.

> Dataset availability and preprocessing is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- Number of dataset file candidates weight: 0.2
- Mentioned dataset file candidates in source-code weight: 0.6
- Dataset file candidates found in source-code in relation to all found weight: 0.2


## RANDOM SEED FEEDBACK

Percentage of random seed lines with fixed seed rating (score: 0.72 out of 1.0): We found that 71.84% of the 103 found random seed declaration lines had a fixed seed. If the value is not 100% make sure to fix the random seeds.


## MODEL SERIALIZATION FEEDBACK

Model serialization rating (score: 1.0 out of 1.0): Model serialization artefacts found. Model serialization helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken.


## HYPERPARAMETER DECLARATION FEEDBACK

Hyperparameter declaration rating (score: 1.0 out of 1.0): We found 4 hyperparameter declaration indicator(s) in the source code. We determined that 1 hyperparameter declaration indicators are a good value. Documenting changes of the hyperparameters helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken.


## OUT-OF-THE-BOX BUILDABILITY FEEDBACK

Out-of-the-box buildability rating (score: 0 out of 1.0): Tested building the repository with BinderHub was not successful because the provided BinderHub URL was not reachable. If you have no access to your own BinderHub deployment you can use the free and publicly available infrastructure accessible under https://www.mybinder.org to test. Please try if it builds successfully, as it greatly helps reproducing the found results. If you have included a Dockerfile in your repository it may not be compatible with BinderHub. Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html

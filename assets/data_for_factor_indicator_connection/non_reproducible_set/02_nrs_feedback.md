# REPRODUCIBILITY FACTOR SCORING (from 0 to 1): 

| Reproducibility factor | Score |
| ----------- | ----------- |
| Source-code availability and documentation |  0.1 |
| Software environment |  0.2 |
| Dataset availability and preprocessing |  0 |
| Random seed |  0 |
| Model serialization |  0 |
| Hyperparameter logging |  0 |
| Out-of-the-box buildability |  0 |


## SOURCE CODE AVAILABILITY AND DOCUMENTATION FEEDBACK

1. License scoring (score: 0 out of 1.0): No license information found. Providing a licenses helps others to tell if your project and its dependencies are available to them.

2. README scoring (score: 0 out of 1.0): No README file(s) found. You should add one to document your repository. We expect from a good README to have at least 82 lines. Make sure to also add useful links e.g. a paper link. We determined that 4 or more accessible links are best. Make also sure that all provided links are correct and reachable. Also add a binder badge if possible (see out-of-the-box buildability feedback.)

3. Source-code pylint scoring (score: 0.0 out of 1.0): Not normalized pylint rating is -7.0 where 10.0 is best. We found that readable code is best for reproducibility and consider ratings over 5.71 as desirable.

4. Source-code-comment-ratio scoring (score: 1.0 out of 1.0): We measured a average ratio of 0.77. We consider a ratio below 8.73 as best. But more comments are fine too (which would make the ratio smaller). Well documented code is important.

> Source-code availability and documentation is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:

- License weight: 0.3
- Readme weight: 0.5
- Sub-readme: Length weight: 0.8
- Sub-readme: Average accessible links weight: 0.2
- Pylint rating weight: 0.1
- Code-comment-ratio weight: 0.1


## SOFTWARE ENVIRONMENT FEEDBACK

> Config file(s) scoring (score: 0 out of 0.8): No Config file(s) detected but we found 5 relevant source code imports which should be included in an configuration file. You should add one (e.g. requirements.txt, config.env, config.yaml, Dockerfile) in order for others to reproduce your repository with the same software environment. We expect from a good config file to strictly specify all library versions and to cover all of the relevant libraries used in the source code. Relevant libraries are ones not included in the Python Standard Library (see: https://docs.python.org/3/library/) or local Python modules.

- Public available libraries in source code file(s) scoring (score: 0.2 out of 0.2: We expect all of the not local modules or standard python libraries to be publicly available. We found that 100.0% are publicly available. We tested if the used library imports are accessible on https://pypi.org. If the score is not 0.2 (=100%): Please try avoiding the use of not public libraries as third parties may not be able to use your repository. Please note: It is also possible that, if the score is not the maxima, all libraries are publicly available, but we could not find a match. If you are unsure please recheck manually.

> Software environment is calculated from the above identifiers. Since these have a different influence on the overall result, they are weighted as follows:
- Source-code imports in config file weight: 0.6
- Strict dependency declarations in config file weight: 0.2
- Public libs in source code weight: 0.2

> Important note: For our analysis we exclude python standard libraries (see: https://docs.python.org/3/library/) as well as local file imports. We also eliminate duplicates (if one import occurs in multiple files we count it as one).


## DATASET AVAILABILITY AND PREPROCESSING FEEDBACK

Dataset availability and preprocessing scoring (score: 0 out of 1.0): No dataset file candidate(s) are mentioned in the source code or referenced within the README. If you have provided a dataset in your repository move it in a folder named "data" or rename the dataset with "data" in name. You should always provide a dataset (if possible) in the repository in order for others to reproduce your repository with the same input data. Linking the dataset in the README is an option, but it can not be guaranteed that the dataset will be accessible in the future so this (usually) not the best solution (except if you deal with large datasets). If you have linked the dataset in the README but the tool has not detected it, move it into an separate section with "data" in the name and provide the name of the dataset as well as the link to it.

> Dataset preprocessing detection is currently not implemented. But: If you preprocessed the dataset in any way please make sure to include either the final dataset or files to reproduce the steps taken.


## RANDOM SEED FEEDBACK

Random seed scoring (score: 0.0 out of 1.0): No random seed declaration(s) found in the source-code. This results in the worst score, as we assume that the random number generator has different starting points each time.If you have declared a random seed but we were not able to detect it, make sure to fix the value of it in order for others to use the same seed.If you have not declared a seed please do so, and assign a specific value to it.


## MODEL SERIALIZATION FEEDBACK

Model serialization scoring (score: 0 out of 1.0): No model serialization artifacts found. Model serialization helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken. We look for one of the following: a) folders named ".dvc", b) files with the extensions ".dvc", ".h5", ".pkl" or ".model" c) one of the following keywords in the source code: "torch.save()", "pickle.dump" or "joblib".


## HYPERPARAMETER LOGGING FEEDBACK

Hyperparameter logging scoring (score: 0 out of 1.0): No hyperparameter logging indicators found. We look out for imports of the following libraries in the source code: "wandb", "neptune", "mlflow" and "sacred". These libraries enable the logging of these parameters in order to document them. Also, we are looking for method calls of these libraries regarding logging. Logging changes of the hyper-parameters helps in the field of machine learning, where incremental improvements should be documented in order for others to understand the steps taken.


## OUT-OF-THE-BOX BUILDABILITY FEEDBACK

Out-of-the-box buildability scoring (score: 0 out of 1.0): Tested building the repository with BinderHub resulted in an error. Repository is not buildable with BinderHub. Please try fixing this, as it greatly helps reproducing the found results. You can use the free and publicly available infrastructure accessible under https://www.mybinder.org to test. If you have included a Dockerfile in your repository it may not be compatible with BinderHub. Check: https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html

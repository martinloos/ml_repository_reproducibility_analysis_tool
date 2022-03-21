[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)]() 

# Machine Learning Repository Reproducibility Analysis

## _- Supporting tool for researchers and reviewers -_
\
This tool helps authors and developers of machine learning experiments as well as reviewers of third-party work. The aim is to increase the probability of reproducibility or to be able to estimate where possible problem areas are. As a result, high quality with regard to reproducibility can be ensured during development or before publication without great additional effort. In addition, a reviewer can quickly and easily examine properties of a machine learning repository in relation to reproducibility.

This is made possible by the approach described in the [paper](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/thesis.pdf) for connecting reproducibility factors with software-based recognition indicators. In simplified terms, this is done using the following approach:

1. Analysis of relevant indicators regarding the reproducibility of a machine learning repository
2. Based on the results of the analysis of two different sets of ML repositories (one containing reproducible and the other non-reproducible repositories), relevant indicators are identified. Representative values ​​and weighting are then assigned to these relevant indicators using statistical and heuristic methods. The analysis results of both sets can be viewed [here](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/representative_indicator_value_extraction_sets).
3. These values ​​can then be used to compare the measured values ​​with the representative ones when analyzing an ML repository. Because the values ​​can have different ranges, we use range normalization to merge these intermediate indicator scores into an overall score for one factor.
4. Based on the intermediate results of the indicators and the overall result of a factor, the tool can then provide feedback that can be used to increase the reproducibility probability.

Restrictions & Assumptions
---------------------
This **tool** was created as part of my bachelor thesis and serves as a **proof of concept**. It is therefore also subject to the following restrictions and assumptions.

1. A public repository hosted by GitHub is expected as input.
2. We are using the "master" branch as default. If not present the tool looks for a "main" branch. If both not found, the tool does not work.
3. Only source code files with the file extension .py (Python) and .ipynb (Python Notebook) are currently supported.
4. We expect the used data set(s) to be in the repository. From a reproducibility point of view, linking to external data sets is not optimal, as it cannot be guaranteed that these will also be available in the future.
5. Since the structure of a repository can vary greatly, the tool cannot always determine a property with 100% certainty. We describe additional details on this in the generated feedback file.

Setup
---------------------
Works with **Python versions from 3.6.2+ to 3.7.13** (higher versions may also work, but the we recommend these).
We used Ubuntu 18.04 LTS and 20.04 LTS as the operating system.
You can check your Python version using the terminal command:
 
```
$ python -V
```

Since the tool uses the functionality of **cURL**, this must also be installed.
You can check your cURL version using the terminal command: 

```
$ curl -V
```

Then, you need to **download** this repository in order to be able to run the code locally.

```
$ git clone https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool.git
```

**Change** the **working directory** to the downloaded folder

```
$ cd ~/<path_to_repository>/ml_repository_reproducibility_analysis_tool
```

After the steps described have been carried out, **install** the remaining **dependencies**: 

```
$ "pip install -r requirements.txt".
```

Then only the following **two modifications have to be made**:

1. Change the csv_path in the [main.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/main.py#L31) file (the generated output files will be saved under this path).

2. Replace the stored BinderHub IP with the IP or URL of your BinderHub in the [binderhub_call.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/binderhub_call.py#L11) file. This configuration is optional. The tool will still work if you don't have a BinderHub deployed. Note the additional information on this in the feedback file.

> Don't forget to save these changes.

Usage
--------------------------
This tool is command line based (possible commands below).

For a detailed description, execute the following command. Then, an overview of the options available should be shown to you.

```
$ python3 main.py -h
```

To start **analyzing a repository**, run the following command.

```
$ python3 main.py -u <repository_url>
```

> Reminder: The repository must be hosted by GitHub.

With the following command you will get **additional information** in your command line (not saved in the result and/or feedback file).

```
$ python3 main.py -u <repository_url> -v
```

Output
--------------------------
This tool produces output in 3 different places.

**Command line**: The intermediate results of each analysis step are displayed in the command line. This information can be used, among other things, for debugging purposes if something goes wrong.

**Result file**: The measured values ​​for all examined indicators and additional data points are saved in the result CSV file.

**Feedback file**: Based on the measured indicator values, feedback is provided for the reproducibility factors (and the individual indicators). This is done in text form as well as through a scoring value.

The result and the feedback file are saved under the specified output path (default: "/tmp").

Sample output files can be viewed [here](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/example_output).

Architecture
--------------------------
In order to explain the interaction and the order of execution of the individual source code files, we describe the tool architecture using the following flow chart. In addition, we briefly describe the function of each file in a simplified form.

![Tool flow chart](/images/flowchart.png?raw=true)

**[main.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/main.py)**: Entry point. Processes the terminal command and executes each source code file in the order described in the flowchart.

**[repository_cloner.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/repository_cloner.py)**: Downloads the provided GitHub repository locally to the "/tmp" folder if not already present there.

**[filter_repository_artefacts.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/filter_repository_artefacts.py)**: Analyses the locally downloaded repository and stores lists of relevant files and directories.

**[readme_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/readme_analysis.py)**: Analyses the identified readme file(s) from filter_repository_artefacts.py. Stores the result of the readme analysis.

**[license_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/license_analysis.py)**: Analyses the identified license file(s) from filter_repository_artefacts.py. Stores the result of the license analysis.

**[dataset_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/dataset_analysis.py)**: Analyses the identified dataset file(s) and folder(s) from filter_repository_artefacts.py. Stores possible dataset candidates, which later will be checked if they are mentioned in the source code file(s).

**[source_code_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/source_code_analysis.py)**: Analyses the identified source code file(s) from filter_repository_artefacts.py. Stores the overall result of the source code file(s) analysis. Note: Other source code type analysis files (e.g. C, R, Java, etc.) should be plugged in here, in case one wants to support them.

**[python_source_code_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/python_source_code_analysis.py)**: This file will be called by source_code_analysis.py for each identified .py or .ipynb file. Converts .ipynb to .py file using nbconvert and performs analysis of the python file. Returns the analysis result.

**[dataset_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/dataset_analysis.py)**: Building the dataset result based on the analysis result of the source_code_analysis.py file where we check for each source code file wether or not a dataset file candidate is mentioned. Stores the result of the dataset analysis.

**[config_files_analysis.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/config_files_analysis.py)**: Analyses the identified configuration file(s) from filter_repository_artefacts.py. Uses result of source_code_analysis.py regarding source code imports. Stores the result of the config file(s) analysis.

**[binderhub_call.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/binderhub_call.py)**: Tries to build the provided GitHub repository using the configured BinderHub IP/URL. Can result in three different results: BinderHub not reachable, not buildable or buildable. Stores the result.

**[result_builder.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/result_builder.py)**: Collects the individual partial results and creates an overall result. This will be saved in the result CSV file.

**[feedback_builder.py](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/feedback_builder.py)**: Collects the individual partial results and creates an overall result. This will be saved in the result CSV file. Extracts the relevant indicators from the overall analysis result of result_builder.py. These results are used to score each factor. This is based on the indicators associated with a factor and the factor-indicator-connection approach described in the paper. Feedback is generated for each factor and its associated indicators and stored in the feedback .md file.

## License

[MIT](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/LICENSE)

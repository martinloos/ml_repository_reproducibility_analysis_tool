# Machine Learning Repository Reproducibility Analysis

## _- Supporting tool for researchers and reviewers -_
\
Placeholder for a description of the problem that is to be solved and a reference to my bachelor thesis

> Note: This tool is not in its final state and not all functions are supported yet.

Requirements
---------------------
Accoring to [GitPython Docs](https://gitpython.readthedocs.io/en/3.1.24/intro.html) Python version >= 3.7 is required. 

Installation
---------------------
First, you need to **download** this repository in order to be able to run the code locally.

```
$ git clone https://https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool.git
```

Then go into the downloaded folder

```
$ cd ~/yourpath/ml_repository_reproducibility_analysis
```

To ensure that the software tool works correctly, you should use the specified library versions.

```
$ pip install -r requirements.txt
```

Usage
--------------------------

From here **you have several options**. For a detailed description, execute the following command.


```
$ python3 main.py -h
```

Then, an overview of the options available should be shown to you.

To start **analyzing a repository**, run the following command.

```
$ python3 main.py -u <Repository URL>
```

You will get information about the analyzed repository in your command line. In addition, the results are recorded in a .csv file.

With the following command you will get **additional information** in your command line. These are not saved in the .csv file.

```
$ python3 main.py -u <Repository URL> -v
```

## License

[MIT](https://git.fim.uni-passau.de/loosmartin/ml_repository_reproducibility_analysis_tool/-/blob/master/LICENSE)
# Machine Learning Repository Reproducibility Analysis

## _- Supporting tool for researchers and reviewers -_
\
Placeholder for a description of the problem that is to be solved and a reference to my bachelor thesis

> Note: This tool is not in its final state and not all functions are supported yet.

Installation
---------------------
First, you need to **download** this repository in order to be able to run the code locally.

```
$ git clone https://INSERT URL
```

Then go into the downloaded folder

```
$ cd ~/yourpath/ml_repository_reproducibility_analysis
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

[MIT](license URL)
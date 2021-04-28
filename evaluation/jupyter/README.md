# Description of folder content `./evaluation/jupyter`

This folder contains all statistical and visual evaluations in the form of Jupyter Notebooks (and some files used for parsing of the raw data).

## Which files should I look at?

If one wants to see all results obtained during the experiments one should have a look at the files `./evaluation/jupyter/evaluate_*.ipynb`.
These can be viewed as precompiled Jupyter Notebook. These files are already precompiled for easy inspection.
In some cases (when only JSON code appears) it might be necessary to click `Display the rendered blob` in github.
A detailed description of the source code and analytical steps taken is contained in each notebook.

## What are the other files of the folder?

* The files `empirical.py`, `plots.py`, and `test_distribution.py` were used to outsource functionality from the notebooks for a cleaner presentation.
These files are used for the statistical tests and plotting of the various diagram types.

## The Jupyter Notebooks do not run on my machine: Some csv-files are not found

Please extract all `tar.xz` archives in the subfolders of `./experiments`.

# Supplementary data of "Evidence for Long-Tails in SLS Algorithms"

This repository contains all data produced for the empirical evaluations of the paper "Evidence for Long-Tails in SLS Algorithms" of Florian Wörz and Jan-Hendrik Lorenz.

The instances used to obtain this data can be found in the Zenodo repository specified in the paper: https://doi.org/10.5281/zenodo.4715893.

## General Folder Structure

The repository contains the following directories/files.
Here, we briefly describe the contents of each folder.
Furthermore, all important folders contain a description file which gives more details.

* `./evaluation`

	Contains the evaluation (via Jupyter Notebooks) of the collected data.
	This is the most important folder.
	All evaluations take place in the files `./evaluation/jupyter/evaluate_*.ipynb`.

* `./experiments`

	Contains all csv data files used for analysis. These files constitute the aggregated raw data.

* `./scripts.tar.xz`

	Contains scripts used for data clean-up of the original collected data and for generating the instances.
	

## Authors

Florian Wörz, Universität Ulm, Institut für Theoretische Informatik, Ulm, Germany

Jan-Hendrik Lorenz, Universität Ulm, Institut für Theoretische Informatik, Ulm, Germany

## Acknowledgments

The authors acknowledge support by the state of Baden-Württemberg through bwHPC.

Florian Wörz was supported by the Deutsche Forschungsgemeinschaft (DFG) under project number 430150230, "Complexity measures for solving propositional formulas".

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

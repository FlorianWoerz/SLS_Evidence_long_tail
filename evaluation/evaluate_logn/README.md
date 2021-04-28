# Description of folder content `./evaluation/evaluate_logn/`

This folder contains the file "all.cvs" that summarizes the goodness-of-fit results for **all** conducted experiments.

## How To Read the .csv-file

To clearly see the structure of the file it should be opend with Excel / LibreOffice Calc / etc.
Here `type` refers to the solver used.
Furthermore, `instance` refers to the path (inside of `./experiments`) to the csv-file containing all data of the respective instance.
We also recorded `p_orig`, the chi-squared p-value; as well as `p_new`, the adjusted p-value according to the bootstrap test described in the paper.


| type    | instance / corresponding cs                                                      | p_orig             | p_new |
|---------|----------------------------------------------------------------------------------|--------------------|-------|
| SRWA    | csvs_factoring/n146/factor_seed3358904958101883040_minn128_maxn256_composite.csv | 0.7466741280021799 | 0.74  |
| SRWA    | csvs_factoring/n146/factor_seed8975071664002667775_minn128_maxn256_composite.csv | 0.4833242449016112 | 0.55  |
|   ...   |              ...                                                                 |   ...              |  ...  |
| probSAT | csvs_probSAT/gen_n300_m1280_k3SAT_seed2999771048.csv                             | 0.7524938299854597 | 0.75  |


## Where can the corresponding scripts be found that calculate these values?

All scripts are located in the `./scripts` folder.
You can find this tool under `scripts/check_logn/test_distribution.py` and `scripts/check_logn/check.py`.

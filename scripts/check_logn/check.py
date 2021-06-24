# This file writes the ./evaluation/evaluate_logn/all.csv file that reports the goodness-of-fit parameters
# (both \chi^2 as well as bootstrapped) for all experiments conducted.

from glob import glob
import pandas as pd
import numpy as np
import os
from scipy.stats import lognorm, norm, chisquare

from empirical import *
from test_distribution import *


if __name__ == "__main__":
	base_path = '../../experiments/'
	file_path = "../../evaluation/evaluate_logn/all.csv"
	seed = 1
	np.random.seed(seed)
	with open(file_path, 'w') as f:
		files = glob(base_path + '**/*.csv', recursive=True)

		for name in files:
			df = pd.read_csv(name, index_col=[0,1])
			df.drop(index=['seed', 'runtime'], level=1, inplace=True)
			if df.empty:
				print(name, 'DataFrame is empty!')
				continue
			s = pd.DataFrame()
			s["mean"] = df.mean(axis=1)
			s["var"] = df.var(axis=1)
			s = s.sort_values(by=['mean'])
			means = s['mean']
			variances = s['var']


			data = means
			m = minimize_nnlf(data, 0.0, data[0]-0.001)
			data = data - m 
			s, loc, scale = lognorm.fit(data, floc=0)
			rv_with_loc = lognorm(s, m, scale)

			p_orig = test_lognormal(means, Q=int(len(means)/5))[1]
			if p_orig <= 0.15:
				N = 1000
			else:
				N = 100
			p_new = compare_mod_chisquare(p_orig, rv_with_loc, means, variances, N=N)

			clean_name = name.replace(base_path, "")
			if "probSAT" in clean_name:
				instance_type = "probSAT"
			elif "YAL" in clean_name:
				instance_type = "YAL"
			else:
				instance_type = "SRWA"

			write_string = f"{instance_type},{clean_name},{p_orig},{p_new}\n"
			print(write_string)
			f.write(write_string)

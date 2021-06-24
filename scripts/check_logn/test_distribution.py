# This file contains the functions used for the goodness-of-fit tests.

import numpy as np
from scipy.stats import lognorm, norm, chisquare

from empirical import *

def test_lognormal(data, Q=1000):
    m = minimize_nnlf(data, 0.0, data[0]-0.0001)
    data_shifted = data - m 
    s, loc, scale = lognorm.fit(data_shifted, floc=0)
    rv = lognorm(s,m,scale)
    
    intervals = [0.0]
    for i in range(1,Q):
        intervals.append(rv.ppf(i/Q))
    intervals.append(np.inf)
    hist = np.histogram(data, bins=intervals)[0]
    
    x_old = 0.0
    buckets = []
    for i in range(1,len(intervals)):
        x = intervals[i]
        interval_prob = rv.cdf(x)-rv.cdf(x_old)
        buckets.append(interval_prob * 5 * Q)
        x_old = x
    return chisquare(hist, f_exp=buckets, ddof=3)

def compare_mod_chisquare(p_orig, rv_with_loc, means, variances, N=100, print_p=False):
	greater_count = 0
	for count in range(N):
	    sample = rv_with_loc.rvs(size=len(means))
	    sample = np.sort(sample)
	    final_samples = []
	    for i in range(len(sample)):
	        x = sample[i]
	        std = np.sqrt(variances[i])/10
	        x += norm.rvs(loc=0.0, scale=std)
	        x = max(x, 1.0)
	        final_samples.append(x)
	    final_samples = np.sort(final_samples)
	    p = test_lognormal(final_samples, Q=int(len(final_samples)/5))[1]
	    if p_orig >= p:
	        greater_count += 1
	        
	    if print_p:
	        print(count, p)
	        
	return greater_count/N

def mod_chisquare(rv_with_loc, means, variances, N=100, print_p=False):
	p_orig = test_lognormal(means)[1]
	p_new = compare_mod_chisquare(p_orig, rv_with_loc, means, variances, N=N, print_p=print_p)
	return p_orig, p_new

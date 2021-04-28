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
        buckets.append(interval_prob * 5000)
        x_old = x
    return chisquare(hist, f_exp=buckets, ddof=3)

def mod_chisquare(rv_with_loc, means, variances, N=100, print_p=False):
	p_orig = test_lognormal(means)[1]
	greater_count = 0

	print("orig", p_orig)
	for count in range(N):
	    sample = rv_with_loc.rvs(size=5000)
	    sample = np.sort(sample)
	    final_samples = []
	    for i in range(len(sample)):
	        x = sample[i]
	        std = np.sqrt(variances[i])/10
	        x += norm.rvs(loc=0.0, scale=std)
	        final_samples.append(x)
	    final_samples = np.sort(final_samples)
	    p = test_lognormal(final_samples)[1]
	    if p_orig >= p:
	        greater_count += 1
	        
	    if print_p:
	        print(count, p)
	        
	print(f"fraction of greater counts: {greater_count/N}")

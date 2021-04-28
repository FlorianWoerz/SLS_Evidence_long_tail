from scipy.optimize import minimize_scalar
from scipy.stats import probplot, lognorm, johnsonsb
from numpy import sort, log, log10, arange, nan, asarray
from numpy.random import choice
from scipy.interpolate import interp1d
import pandas as pd


def ecdf_old(x):
    x = sort(x)
    n = float(len(x))
    y = []
    for i in x:
        y.append(len(x[x <= i])/n)
    return y


def e_survival_old(x):
    x = sort(x)
    n = float(len(x))
    y = []
    for i in x:
        y.append(1-len(x[x < i])/n)
    return y

def ecdf(x):
    # c = 1.0/len(x)
    # return arange(c, 1.0 + c, c)
    x = sort(x)
    n = float(len(x))
    y = []
    for i in x:
        y.append(len(x[x <= i])/n)
    return asarray(y)


def e_survival(x):
    y = 1.0 - ecdf(x)
    y[-1] = nan
    return y


def r_lognormplot(data, i):
    _, y = probplot(log10(data - i))
    return log(1 - y[2])


def minimize_r_lognormplot(data, lower, upper):
    return minimize_scalar(lambda i: r_lognormplot(data, i), bounds=(lower, upper), method='Bounded').x


def nnlf(data, i):
    params=lognorm.fit(data, floc=i)
    return lognorm.nnlf(params, data)


def minimize_nnlf(data, lower, upper):
    return minimize_scalar(lambda i: nnlf(data, i), bounds=(lower, upper), method='Bounded').x

def SB_nnlf(data, i):
    params=johnsonsb.fit(data, floc=i)
    return johnsonsb.nnlf(params, data)

def SB_minimize_nnlf(data, lower, upper):
    return minimize_scalar(lambda i: SB_nnlf(data, i), bounds=(lower, upper), method='Bounded').x

def resample(sample, ncols=101):
    """Generate bootstrap samples.
    """
    nrows = len(sample)
    array = sort(choice(sample, (nrows, ncols)), axis=0)
    return pd.DataFrame(array)

def get_surv_confidence(sample, n=101):
    """Provides a 90% confidence interval for a survival curve.
    """
    samples = resample(sample, ncols=n)
    df = pd.DataFrame(index=sample, columns=samples.columns)
    for i in samples.columns:
        y = 1.0 - ecdf(samples[i])
        s = interp1d(samples[i], y, kind="previous", assume_sorted=True, bounds_error=False, fill_value=(1.0, 0.0))
        df[i] = s(sample)
    
    df.values.sort()
    return df

def get_cdf_confidence(sample, n=101):
    """Provides a 90% confidence interval for a cdf.
    """
    samples = resample(sample, ncols=n)
    df = pd.DataFrame(index=sample, columns=samples.columns)
    for i in samples.columns:
        y = ecdf(samples[i])
        s = interp1d(samples[i], y, kind="previous", assume_sorted=True, bounds_error=False, fill_value=(0.0, 1.0))
        df[i] = s(sample)
    
    df.values.sort()
    return df

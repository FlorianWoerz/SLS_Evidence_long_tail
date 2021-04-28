import numpy as np
import scipy.stats as stats
from scipy.stats import lognorm
from matplotlib import pyplot as plt

from empirical import *

def plot_shift_lognormplots(data, xmin, xmax, plot = True):
    r_values = []
    for i in range(xmin, xmax+1):
        x = np.log10(data - i)
        _, y = stats.probplot(x)
        r_values.append(1-y[2])
    if plot:
        plt.figure()
        plt.plot(r_values)
        plt.yscale('log')
    return np.argmin(r_values)


def plot_shift_nnlf(data, xmin, xmax, plot = True):
    r_values = []
    for i in range(xmin, xmax+1):
        params=lognorm.fit(data, floc=i)
        r_values.append(lognorm.nnlf(params, data))
    if plot:
        plt.figure()
        plt.plot(r_values)
    return np.argmin(r_values)

def plot_and_compare_cdf(data, rv, suptitle=None, plot_confidence=False):
    fig = plt.figure(figsize=(20,7))
    plt.subplot(1,3,1)
    plt.plot(data, ecdf(data), marker='.', markersize=4, color='r')
    plt.plot(data, rv.cdf(data), color='b')
    if plot_confidence:
        df = get_cdf_confidence(data)
        nrows, ncols = df.shape
        low = int(ncols * 0.025)
        high = int(ncols * 0.975)
        plt.fill_between(df.index, df[low], df[high], alpha=0.2)
    plt.xscale('log')
    plt.yscale('log')
    plt.ylim(2*10**(-4),1.05)
    plt.grid(True)

    plt.subplot(1,3,2)
    plt.plot(data, ecdf(data), color='r')
    plt.plot(data, rv.cdf(data), color='b')
    plt.ylim(-0.01,1.01)
    plt.grid(True)

    plt.subplot(1,3,3)
    plt.plot(data, e_survival(data), marker='.', markersize=4, color='r')
    plt.plot(data, rv.sf(data), color='b')
    if plot_confidence:
        df = get_surv_confidence(data)
        nrows, ncols = df.shape
        low = int(ncols * 0.025)
        high = int(ncols * 0.975)
        plt.fill_between(df.index, df[low], df[high], alpha=0.2)
    plt.xscale('log')
    plt.yscale('log')
    plt.ylim(2*10**(-4),1.05)
    plt.grid(True)
    if suptitle is not None:
        fig.suptitle(suptitle, fontsize=20)
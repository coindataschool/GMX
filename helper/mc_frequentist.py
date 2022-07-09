from distfit import distfit
import random
import pandas as pd

def mc_frequentist(xs, n_fut=120, n_iter=1000, random_seed=42, show_plot=True):
    """ Generates Monte Carlo samples using (frequentist) parametric distributions.

    Automatically selects a distribution that best fit to the observed data, 
    with parameter values estimated from the observed data. Then it generates 
    random samples from this distribution for each future period. 

    It uses the distfit package: https://erdogant.github.io/distfit/pages/html/index.html
    
    Arguments:
    xs -- a series or array of historical observations, for example, daily log returns.
    n_fut -- integer. How many future time periods (default = 120) do you 
        want to simulate? The unit of time periods is determined by the 
        frequency of the historical observations. For example, if data are 
        daily, it's the number of future days. If yearly, it's the number of 
        future years. 
    n_iter -- integer. How many samples (default = 1000) do you want to draw 
        at each future time period. 
    random_seed -- integer. Seed for the random number generator. Default = 42.
    show_plot -- logical. Whether to show the best fitted distribution plot 
        (default = True). Showing the plot will make users understand what 
        distribution was chosen.
    """
        
    # initialize
    dist = distfit(todf=True)
    
    # search for best theoretical fit for your empirical data
    _ = dist.fit_transform(xs)

    if show_plot:
        dist.plot();

    # use the best fitted distribution to simulate data for `n_fut` future 
    # periods (assuming indepedence) and repeat `n_iter` times.
    random.seed(random_seed)
    df_fut = pd.DataFrame({
        "iter{}".format(i): dist.generate(n=n_fut, verbose=False) 
        for i in range(1, n_iter+1)})
    
    return df_fut


# # change to long format
# fut_vals = df_fut.stack()
# fut_vals.name = xs.name

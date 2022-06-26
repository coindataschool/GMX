from statsmodels.tsa.deterministic import DeterministicProcess

def mk_X_linear_trend(dates):
    """Create design matrix based off dates to be used for fitting a linear regression.
    
    Arguments:
    dates -- an index or a list of 'datetime64[ns]' objects
    """
    dp = DeterministicProcess(
        index=dates,
        constant=False, # cuz scikit-learn linear regression fits the intercept by default
        order=1,
        drop=True
    )
    return dp.in_sample()

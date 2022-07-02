from statsmodels.tsa.deterministic import DeterministicProcess
import pandas as pd

def mk_X_linear_trend(dates):
    """Create design matrix for fitting a linear regression.
    
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


def mk_X_trend_seasonality(dates, order=1, include_default_seasonality=True):
    """Create design matrix for fitting a linear regression.
    
    Arguments:
    dates -- an index or a list of 'datetime64[ns]' objects
    """
    dp = DeterministicProcess(
        index=dates,
        constant=False, # cuz scikit-learn linear regression fits the intercept by default
        order=order,
        seasonal=include_default_seasonality,
        drop=True
    )
    return dp.in_sample()


def make_lags(ts, lags, lead_time=1, name='y'):
    return pd.concat(
        {
            f'{name}_lag_{i}': ts.shift(i)
            for i in range(lead_time, lags + lead_time)
        },
        axis=1)

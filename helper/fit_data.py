from sklearn.linear_model import LinearRegression
import pandas as pd

def fit_linreg(X, y):
    linreg = LinearRegression().fit(X, y)
    intercept = linreg.intercept_
    slope = linreg.coef_[0]
    print("intercept: {}".format(intercept), "slope: {}".format(slope))
    yhat = linreg.predict(X)
    return dict(yhat=pd.Series(yhat, index=y.index), slope=slope)
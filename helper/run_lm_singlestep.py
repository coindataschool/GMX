from sklearn.model_selection import train_test_split
import sklearn.metrics as metrics
from sklearn.linear_model import LinearRegression
import pandas as pd

def run_lm_singlestep(X, y, test_size=0.2, verbose=True):
    """ Train a linear regression that does a 1-step forecast (i.e., predict
    the target for the next time step). Evaluate model's performance 
    on both the training and test sets.

    Arguments:
    X -- 2D numpy array or pandas frame that contains feature values. Must NOT 
         contain a column of 1's because when calling LinearRegression(), it 
         automatically add the constant term by default.
    y -- 1D numpy array or pandas series. 
    test_size -- percent of data for testing. Default is 0.2.

    Returns
    -------
    A tuple of two elements. The first element is the residuals on training 
    set, and the second element is the residuals on the test set.
    """
    # split data, do NOT shuffle! Need to preserve time order.
    X_train, X_test, y_train, y_test = \
        train_test_split(X, y, test_size=test_size, shuffle=False) 
    
    # train a linear regression, constant is added automatically by default
    # so no need to include a constant term in X_train.
    model = LinearRegression().fit(X_train, y_train) 

    # evaluate model on both training and test sets
    yhat_train = pd.Series(model.predict(X_train), index=X_train.index)
    yhat_test = pd.Series(model.predict(X_test), index=X_test.index)
    train_rmse = metrics.mean_squared_error(yhat_train, y_train, squared=False)
    test_rmse = metrics.mean_squared_error(yhat_test, y_test, squared=False)
    
    if verbose:
        print((f"Train RMSE: {train_rmse:.2f}\n" f"Test RMSE: {test_rmse:.2f}"))
        
    return y_train, yhat_train, y_test, yhat_test
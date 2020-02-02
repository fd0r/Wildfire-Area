from sklearn.ensemble import RandomForestRegressor
from sklearn.base import BaseEstimator
import numpy as np

class Regressor(BaseEstimator):
    def __init__(self):
        pass

    def fit(self, X, y):
        pass

    def predict(self, X):
        n = X.shape[0]
        y_pred = 0.001*np.ones(n)
        return y_pred

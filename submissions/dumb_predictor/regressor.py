from sklearn.linear_model import LinearRegression
from sklearn.base import BaseEstimator
import numpy as np

class Regressor(BaseEstimator):
    def __init__(self):
        self.reg = LinearRegression(n_estimators=5, max_depth=50, max_features=10)

    def fit(self, X, y):
        self.reg.fit(np.ones(y.shape)*0.001, y)

    def predict(self, X):
        return self.reg.predict(X)

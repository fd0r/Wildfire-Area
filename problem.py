import os

import numpy as np
import pandas as pd
import rampwf as rw
from rampwf.score_types.base import BaseScoreType
from rampwf.workflows import FeatureExtractorRegressor
from sklearn.model_selection import KFold

problem_title = 'Prediction of the surface burned by wildfires in the south of France'
_target_column_name = 'Area'
# A type (class) which will be used to create wrapper objects for y_pred
Predictions = rw.prediction_types.make_regression()


# An object implementing the workflow

class WFA(FeatureExtractorRegressor):
    def __init__(self, workflow_element_names=['feature_extractor', 'regressor']):  # TODO: Add helpful data
        super(WFA, self).__init__(workflow_element_names[:2])
        self.element_names = workflow_element_names


workflow = WFA()


# TODO: define the score (specific score for the WFA problem)

class WFA_error(BaseScoreType):
    is_lower_the_better = True
    minimum = 0.0
    maximum = float('inf')

    def __init__(self, name='wfa error', precision=2):
        self.name = name
        self.precision = precision

    def __call__(self, y_true, y_pred):

        if isinstance(y_true, pd.Series):
            y_true = y_true.values

        alpha = 0.7
        p = 2

        losses = 2*(alpha+(1-2*alpha)*(1*((np.log(y_true)-np.log(y_pred)) < 0)))*((np.log(y_true)-np.log(y_pred))**p)

        loss = np.mean(losses)

        return loss


score_types = [
    WFA_error(name='wfa error', precision=3),
    rw.score_types.RMSE(name='RMSE'),
    rw.score_types.RelativeRMSE(name='Relative RMSE'),
    rw.score_types.NormalizedRMSE(name='Normalized RMSE'),
]


def get_cv(X, y):
    cv = KFold(n_splits=5, shuffle=False)
    return cv.split(X, y)


def _read_data(path, f_name):
    data = pd.read_csv(os.path.join(path, 'data', f_name))
    y_array = data[_target_column_name].values
    X_df = data.drop(_target_column_name, axis=1)
    return X_df, y_array


def get_train_data(path='.'):
    f_name = 'train.csv'
    return _read_data(path, f_name)


def get_test_data(path='.'):
    f_name = 'test.csv'
    return _read_data(path, f_name)

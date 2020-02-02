import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

class FeatureExtractor(object):
    def __init__(self):
        pass

    def fit(self, X_df, y_array):

        def process_date(X):
            date = pd.to_datetime(X['Signal'], format='%Y-%m-%d %H:%M:%S')
            return np.c_[date.dt.year, date.dt.month, date.dt.day,
                         date.dt.hour, date.dt.minute, date.dt.second]
        date_transformer = FunctionTransformer(process_date, validate=False)

        date_col = ['Signal']

        preprocessor = ColumnTransformer(
            transformers=[
                ('date', make_pipeline(date_transformer,SimpleImputer(strategy='median')), date_col),
                ])

        self.preprocessor = preprocessor
        self.preprocessor.fit(X_df, y_array)
        return self

    def transform(self, X_df):
        return self.preprocessor.transform(X_df)

import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline

class FeatureExtractor(object):
    def __init__(self):
        pass

    def fit(self, X_df, y_array):

        def process_insee(X):
            insee_nums = pd.to_numeric(X['INSEE_code'], errors='coerce')
            return insee_nums.values[:, np.newaxis]
        insee_transformer = FunctionTransformer(process_insee, validate=False)

        def process_dep(X):
            dep_nums = pd.to_numeric(X['Department'], errors='coerce')
            return dep_nums.values[:, np.newaxis]
        dep_transformer = FunctionTransformer(process_dep, validate=False)

        def process_origin(X):
            or_nums = pd.to_numeric(X['Origin'], errors='coerce')
            return or_nums.values[:, np.newaxis]
        origin_transformer = FunctionTransformer(process_origin, validate=False)

        numeric_transformer = Pipeline(steps=[('impute', SimpleImputer(strategy='median'))])

        def process_date(X):
            date = pd.to_datetime(X['Signal'], format='%Y-%m-%d %H:%M:%S')
            return np.c_[date.dt.year, date.dt.month, date.dt.day,
                         date.dt.hour, date.dt.minute, date.dt.second]
        date_transformer = FunctionTransformer(process_date, validate=False)

        num_cols = ['ID', 'Year']
        insee_col = ['INSEE_code']
        date_col = ['Signal']
        dep_col = ['Department']
        origin_col = ['Origin']

        preprocessor = ColumnTransformer(
            transformers=[
                ('insee', make_pipeline(insee_transformer,
                                        SimpleImputer(strategy='median')), insee_col),
                ('num', numeric_transformer, num_cols),
                ('date', make_pipeline(date_transformer,SimpleImputer(strategy='median')), date_col),
                ('dep', make_pipeline(dep_transformer,SimpleImputer(strategy='median')), dep_col),
                ('origin', make_pipeline(origin_transformer,SimpleImputer(strategy='median')), origin_col),
                ])

        self.preprocessor = preprocessor
        self.preprocessor.fit(X_df, y_array)
        return self

    def transform(self, X_df):
        return self.preprocessor.transform(X_df)

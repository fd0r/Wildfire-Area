import os
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

        def insee(X):
            insee_nums = pd.to_numeric(X['INSEE'], errors='coerce')
            return insee_nums.values[:, np.newaxis]
        insee_transformer = FunctionTransformer(insee, validate=False)

        def dep(X):
            dep_nums = pd.to_numeric(X['Département'], errors='coerce')
            return dep_nums.values[:, np.newaxis]
        dep_transformer = FunctionTransformer(dep, validate=False)

        def origine(X):
            or_nums = pd.to_numeric(X['Alerteur'], errors='coerce')
            return or_nums.values[:, np.newaxis]
        origine_transformer = FunctionTransformer(origine, validate=False)

        numeric_transformer = Pipeline(steps=[('impute', SimpleImputer(strategy='median'))])

        def process_date(X):
            date = pd.to_datetime(X['Alerte'], format='%Y-%m-%d %H:%M:%S')
            return np.c_[date.dt.year, date.dt.month, date.dt.day,
                         date.dt.hour, date.dt.minute, date.dt.second]
        date_transformer = FunctionTransformer(process_date, validate=False)

        num_cols = ['Numéro', 'Année']
        insee_col = ['INSEE']
        date_col = ['Alerte']
        dep_col = ['Département']
        origine_col = ['Alerteur']

        preprocessor = ColumnTransformer(
            transformers=[
                ('insee', make_pipeline(insee_transformer,SimpleImputer(strategy='median')), insee_col),
                ('num', numeric_transformer, num_cols),
                ('date', make_pipeline(date_transformer,SimpleImputer(strategy='median')), date_col),
                ('dep', make_pipeline(dep_transformer,SimpleImputer(strategy='median')), dep_col),
                ('origine', make_pipeline(origine_transformer,SimpleImputer(strategy='median')), origine_col),
                ])

        self.preprocessor = preprocessor
        self.preprocessor.fit(X_df, y_array)
        return self

    def transform(self, X_df):
        return self.preprocessor.transform(X_df)

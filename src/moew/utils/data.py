import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from torch import nn
from .model import FocalLoss


class TargetPreProcess(BaseEstimator, TransformerMixin):
    def __init__(self, num_classes: int):
        self.n_classes = num_classes

    def fit(self, y: pd.Series):
        if self.n_classes == 1:
            self.y_loss = nn.MSELoss()
            self.avg = y.mean()
            self.std = y.std()
            y = (y - self.avg) / self.std
        else:
            self.y_loss = FocalLoss()
            y = y.astype("category")
            self.mapping = {v: k for k, v in enumerate(y.cat.categories)}

        return self

    def transform(self, y: pd.Series, norm: bool = True):
        if self.n_classes == 1:
            y = (y - self.avg) / self.std if norm else y
        else:
            y = y.map(self.mapping)

        return y


class FeaturePreProcess(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.loss = nn.MSELoss()
        self.norm = dict()
        self.label_encode = dict()

    def fit(self, X: pd.DataFrame):
        # TODO: datetime features and proper dealing with categorical features
        self.col_order = X.columns
        self.num_cols = X.select_dtypes(include=["number"]).columns
        self.cat_cols = X.select_dtypes(include=["object", "category"]).columns

        for col in X.columns:
            if col in self.num_cols:
                avg, std = X[col].mean(), X[col].std()
                self.norm[col] = [avg, std]
            elif col in self.cat_cols:
                X[col] = X[col].astype("category")
                self.label_encode[col] = {
                    v: k + 1 for k, v in enumerate(y.cat.categories)
                }
                avg, std = X[col].mean(), X[col].std()
                self.norm[col] = [avg, std]
            else:
                raise NotImplementedError(f"Got data type: {X[col].dtype}")

        return self

    def transform(self, X: pd.DataFrame, norm: bool = True):
        for col in self.num_cols:
            avg, std = self.norm[col]
            X[col] = (X[col] - avg) / std if nrom else X[col]
        for col in self.cat_cols:
            X[col] = X[col].map(self.label_encode[col]).fillna(0)
            avg, std = self.norm[col]
            X[col] = (X[col] - avg) / std if nrom else X[col]

        return X

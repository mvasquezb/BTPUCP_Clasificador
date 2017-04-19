from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.neighbors import KNeighborsClassifier


class ProxyEstimator(BaseEstimator, ClassifierMixin):
    def __init__(self, estimator=KNeighborsClassifier, **kwargs):
        if isinstance(estimator, type):
            estimator = estimator(**kwargs)
        self.estimator = estimator

    def fit(self, X, y=None):
        return self.estimator.fit(X, y)

    def predict(self, X):
        return self.estimator.fit(X)

    def get_params(self, deep=True):
        return self.estimator.get_params(deep=deep)

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            self.estimator.setattr(parameter, value)
        return self

    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X)

    def transform(self, X):
        return self.estimator.transform(X)

    def score(self, X, y, sample_weight=None):
        return self.estimator.score(X, y, sample_weight)

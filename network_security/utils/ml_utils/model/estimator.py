import os
import sys
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger

class NetworkModel:
    def __init__(self,preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model

    def predict(self, X):
        try:
            x_transformed = self.preprocessor.transform(X)
            y_hat = self.model.predict(x_transformed)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def __repr__(self):
        return f"{type(self.model).__name__}()"

    def __str__(self):
        return f"{type(self.model).__name__}()"
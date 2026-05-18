import yaml
import os
import sys
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger  
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
#import dill
import pickle
from network_security.constant.training_pipeline import SCHEMA_FILE_PATH

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def write_yaml_file(file_path: str, data: dict):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as yaml_file:
            yaml.safe_dump(data, yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
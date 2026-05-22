"""defining common constant for training pipeline   """
import os
TARGET_COLUMN = "Result"
PIPELINE_NAME: str = "network_security" 
ARTIFACT_DIR: str = "Artifact"
FILE_NAME: str = "phisingData.csv"

TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"

SCHEMA_FILE_PATH: str = os.path.join("data_schema", "schema.yaml")

"""
Data ingestion related constant start with DATA_INGESTION VAR NAME
"""
DATA_INGESTION_COLECTION_NAME = "NetworkData"
DATA_INGESTION_DIR_NAME = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR_NAME = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
DATA_INGESTION_DATABASE_NAME = "KRISHAI"

"""
Data Validation related constant start with DATA_VALIDATION VAR NAME
"""
DATA_VALIDATION_DIR_NAME: str = "data_validation"
DATA_VALIDATION_VALID_DIR: str = "validated"
DATA_VALIDATION_INVALID_DIR: str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR: str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"

"""
Data Transformation related constant start with DATA_TRANSFORMATION VAR NAME
"""
import numpy as np
DATA_TRANSFORMATION_DIR_NAME: str = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DIR: str = "transformed"    
DATA_TRANSFORMATION_PREPROCESSOR_DIR: str = "preprocessor"
DATA_TRANSFORMATION_TRAIN_FILE_NAME: str = "train.npy"
DATA_TRANSFORMATION_TEST_FILE_NAME: str = "test.npy"
DATA_TRANSFORMATION_PREPROCESSOR_OBJECT_FILE_NAME: str = "preprocessor.pkl"
## KNN Imputer params to replace missing values with mean of nearest neighbors
DATA_TRANSFORMATION_IMPUTER_PARAMS : dict = {
    "missing_values": np.nan,
    "n_neighbors": 3,
    "weights": "uniform",
}

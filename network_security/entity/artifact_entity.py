from dataclasses import dataclass
from network_security.constant.training_pipeline import *

@dataclass
class DataIngestionArtifact:
    trained_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    valid_train_file_path: str
    valid_test_file_path: str
    drift_report_file_path: str
    schema_file_path: str
    invalid_train_file_path: str = None
    invalid_test_file_path: str = None

@dataclass
class DataTransformationArtifact:
    transformed_train_file_path: str
    transformed_test_file_path: str
    preprocessed_object_file_path: str
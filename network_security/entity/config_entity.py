from datetime import datetime
import os
import sys
from network_security.exception.exception import NetworkSecurityException
from network_security.constant.training_pipeline import (
    PIPELINE_NAME, 
    ARTIFACT_DIR,
    DATA_INGESTION_DIR_NAME,
    DATA_INGESTION_FEATURE_STORE_DIR,
    DATA_INGESTION_INGESTED_DIR_NAME,
    TRAIN_FILE_NAME,
    TEST_FILE_NAME,
    DATA_VALIDATION_DIR_NAME,
    DATA_VALIDATION_VALID_DIR,
    DATA_VALIDATION_INVALID_DIR,    
    DATA_VALIDATION_DRIFT_REPORT_DIR,
    DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
)

class TrainingPipelineConfig:
    def __init__(self, time_stamp = datetime.now()):
        try:
            self.pipeline_name = PIPELINE_NAME
            formatted_time_stamp = time_stamp.strftime("%m_%d_%Y_%H_%M_%S")
            self.artifact_dir = os.path.join(ARTIFACT_DIR, self.pipeline_name, formatted_time_stamp)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e



class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        try:
            # El directorio de ingesta de datos ahora está dentro del directorio de artefactos de la ejecución.
            self.data_ingestion_dir = os.path.join(
                training_pipeline_config.artifact_dir, DATA_INGESTION_DIR_NAME
            )
            self.feature_store_dir = os.path.join(
                self.data_ingestion_dir, DATA_INGESTION_FEATURE_STORE_DIR
            )
            self.ingested_dir = os.path.join(self.data_ingestion_dir, DATA_INGESTION_INGESTED_DIR_NAME)
            self.train_file_path = os.path.join(self.ingested_dir, TRAIN_FILE_NAME)
            self.test_file_path = os.path.join(self.ingested_dir, TEST_FILE_NAME)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        try:
            self.data_validation_dir = os.path.join(
                training_pipeline_config.artifact_dir, DATA_VALIDATION_DIR_NAME
            )
            self.valid_train_file_path = os.path.join(
                self.data_validation_dir, DATA_VALIDATION_VALID_DIR, TRAIN_FILE_NAME
            )
            self.valid_test_file_path = os.path.join(
                self.data_validation_dir, DATA_VALIDATION_VALID_DIR, TEST_FILE_NAME
            )
            self.invalid_train_file_path = os.path.join(
                self.data_validation_dir, DATA_VALIDATION_INVALID_DIR, TRAIN_FILE_NAME
            )
            self.invalid_test_file_path = os.path.join(
                self.data_validation_dir, DATA_VALIDATION_INVALID_DIR, TEST_FILE_NAME
            )
            self.drift_report_file_path = os.path.join(
                self.data_validation_dir, DATA_VALIDATION_DRIFT_REPORT_DIR, DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
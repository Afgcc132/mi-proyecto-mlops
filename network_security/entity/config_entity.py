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
    TEST_FILE_NAME
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
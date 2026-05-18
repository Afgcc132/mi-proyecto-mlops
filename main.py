from network_security.components.data_ingestion import DataIngestion
from network_security.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig
from network_security.exception.exception import NetworkSecurityException
import sys
from network_security.logging.logger import logger
from network_security.components.data_validation import DataValidation
from network_security.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact

if __name__ == '__main__':
    try:
        training_pipeline_config = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logger.info(f"Data Ingestion artifact: {data_ingestion_artifact}")
        data_validation_config = DataValidationConfig(training_pipeline_config=training_pipeline_config)
        data_validation = DataValidation(data_validation_config=data_validation_config, data_ingestion_artifact=data_ingestion_artifact)
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.info(f"Data Validation artifact completed: {data_validation_artifact}")
        print(data_validation_artifact )
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
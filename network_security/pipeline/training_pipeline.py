import os 
import sys
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger
from network_security.components.data_ingestion import DataIngestion
from network_security.components.data_validation import DataValidation
from network_security.components.data_transformation import DataTransformation
from network_security.components.model_trainer import ModelTrainer
from network_security.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,

)

from network_security.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)


class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info("Starting data ingestion component")
            data_ingestion_config = DataIngestionConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            data_ingestion = DataIngestion(data_ingestion_config=data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logger.info("Data ingestion component completed")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact):
        try:
            logger.info("Starting data validation component")
            data_validation_config = DataValidationConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            data_validation = DataValidation(
                data_validation_config=data_validation_config,
                data_ingestion_artifact=data_ingestion_artifact
            )
            data_validation_artifact = data_validation.initiate_data_validation()
            logger.info("Data validation component completed")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact):
        try:
            logger.info("Starting data transformation component")
            data_transformation_config = DataTransformationConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            data_transformation = DataTransformation(data_transformation_config=data_transformation_config,
                data_validation_artifact=data_validation_artifact
            )
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logger.info("Data transformation component completed")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact):
        try:
            logger.info("Starting model trainer component")
            model_trainer_config = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config  
            )
            model_trainer = ModelTrainer(
                model_trainer_config=model_trainer_config,
                data_transformation_artifact=data_transformation_artifact
            )
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logger.info("Model trainer component completed")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        

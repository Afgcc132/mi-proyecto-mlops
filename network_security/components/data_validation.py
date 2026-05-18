from network_security.logging.logger import logger
from network_security.exception.exception import NetworkSecurityException
from network_security.utils.main_utils.utils  import read_yaml_file, write_yaml_file
from network_security.entity.config_entity import DataValidationConfig  
from network_security.entity.artifact_entity import DataValidationArtifact
from network_security.entity.artifact_entity import DataIngestionArtifact
from network_security.constant.training_pipeline import (
    SCHEMA_FILE_PATH,
    TARGET_COLUMN,
    DATA_VALIDATION_DRIFT_REPORT_DIR,
    DATA_VALIDATION_DRIFT_REPORT_FILE_NAME
)

import os
import sys
from scipy.stats import ks_2samp
import pandas as pd
import numpy as np


class DataValidation:
    def __init__(self, data_validation_config: DataValidationConfig, data_ingestion_artifact: DataIngestionArtifact):
        try:
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def validate_number_of_columns(self, df: pd.DataFrame) -> bool:
        try:
            expected_num_columns = len(self.schema_config['columns'])
            actual_num_columns = df.shape[1]
            if expected_num_columns != actual_num_columns:
                logger.error(f"El número de columnas es incorrecto. Se esperaban {expected_num_columns} pero se encontraron {actual_num_columns}.")
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def detect_data_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame) -> str:
        try:
            drift_report = {}
            for column in base_df.columns:
                if column in current_df.columns:
                    statistic, p_value = ks_2samp(base_df[column], current_df[column])
                    drift_report[column] = {
                        "ks_statistic": float(statistic),
                        "p_value": float(p_value),
                        "drift_detected": bool(p_value < 0.05)
                    }
            
            # Usar la ruta del archivo definida en la configuración
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            write_yaml_file(drift_report_file_path, drift_report)
            logger.info(f"Reporte de data drift guardado en: {drift_report_file_path}")

            return drift_report_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_data_validation(self) -> DataValidationArtifact:   
        try:
            # Leer los archivos de entrenamiento y prueba desde el artefacto de ingesta
            train_df = self.read_data(self.data_ingestion_artifact.trained_file_path)
            test_df = self.read_data(self.data_ingestion_artifact.test_file_path)
            
            # Validar el número de columnas
            if not self.validate_number_of_columns(train_df):
                expected_num_columns = len(self.schema_config['columns'])
                actual_num_columns = train_df.shape[1]
                error_msg = (f"El archivo de entrenamiento no tiene el número correcto de columnas. "
                             f"Esperado según schema.yaml: {expected_num_columns}, "
                             f"Encontrado en train.csv: {actual_num_columns}.")
                raise Exception(error_msg)
            if not self.validate_number_of_columns(test_df):
                expected_num_columns = len(self.schema_config['columns'])
                actual_num_columns = test_df.shape[1]
                error_msg = (f"El archivo de prueba no tiene el número correcto de columnas. "
                             f"Esperado según schema.yaml: {expected_num_columns}, "
                             f"Encontrado en test.csv: {actual_num_columns}.")
                raise Exception(error_msg)
            
            # Detectar data drift entre el conjunto de entrenamiento y prueba
            drift_report_file_path = self.detect_data_drift(base_df=train_df, current_df=test_df)

            # Crear el directorio para los datos validados si no existe
            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)

            # Guardar los datos validados usando las rutas de la configuración
            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False)

            data_validation_artifact = DataValidationArtifact(
                validation_status=True,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                schema_file_path=SCHEMA_FILE_PATH,
                drift_report_file_path=drift_report_file_path
            )
            logger.info(f"Artefacto de validación de datos creado: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
        
    
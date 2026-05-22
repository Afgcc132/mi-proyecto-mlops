import sys
import os
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logging
from network_security.entity.config_entity import DataTransformationConfig
from network_security.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
import numpy as np
import pandas as pd 
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline   
from network_security.constant.training_pipeline import (
    DATA_TRANSFORMATION_IMPUTER_PARAMS, TARGET_COLUMN
)
from network_security.utils.main_utils.utils import save_object, save_numpy_array_data

class DataTransformation:
    def __init__(self, data_transformation_config: DataTransformationConfig, 
                 data_validation_artifact: DataValidationArtifact):
        try:
            self.data_transformation_config = data_transformation_config
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def get_data_transformer_object() -> Pipeline:
        try:    
            imputer_params = DATA_TRANSFORMATION_IMPUTER_PARAMS
            imputer = KNNImputer(**imputer_params)
            transformation_pipeline = Pipeline(steps=[
                ('imputer', imputer)
            ])  
            return transformation_pipeline
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            # Leer los datos validados
            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)
            
            # Separar características y etiquetas
            X_train = train_df.drop(TARGET_COLUMN, axis=1)
            y_train = train_df[TARGET_COLUMN]
            y_train= y_train.replace(-1, 0)  # Reemplazar -1 por 0 en las etiquetas de entrenamiento    
            X_test = test_df.drop(TARGET_COLUMN, axis=1)
            y_test = test_df[TARGET_COLUMN]
            y_test = y_test.replace(-1, 0)  # Reemplazar -1 por 0 en las etiquetas de prueba
            
           
            
            # Ajustar el pipeline en los datos de entrenamiento y transformar ambos conjuntos
            transformation_pipeline = self.get_data_transformer_object()
            X_train_transformed = transformation_pipeline.fit_transform(X_train)    
            X_test_transformed = transformation_pipeline.transform(X_test)
            # Combinar las características transformadas con las etiquetas
            train_array = np.c_[X_train_transformed, y_train.to_numpy()]
            test_array = np.c_[X_test_transformed, y_test.to_numpy()]
            
            
            # Guardar los arrays transformados y el objeto preprocesador
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, train_array) 
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, test_array)
            save_object(self.data_transformation_config.preprocessor_object_file_path, transformation_pipeline)


            
            data_transformation_artifact = DataTransformationArtifact(
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
                preprocessed_object_file_path=self.data_transformation_config.preprocessor_object_file_path)
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
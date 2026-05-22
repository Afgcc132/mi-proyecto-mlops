from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger  

"""configaration for data ingestion component"""
from network_security.entity.config_entity import DataIngestionConfig
from network_security.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
import pymongo
from typing import Tuple
from network_security.constant.training_pipeline import (
    FILE_NAME,
    DATA_INGESTION_DATABASE_NAME,
    DATA_INGESTION_COLECTION_NAME,
    DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
)
MONGO_DB_URL = os.getenv("MONGO_DB_URL") # This will now be loaded by main.py

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_collection_as_dataframe(self, collection_name: str, database_name: str) -> pd.DataFrame:
        client = None
        try:
            client = pymongo.MongoClient(MONGO_DB_URL)
            db = client[database_name]
            collection = db[collection_name]
            data = list(collection.find())
            df = pd.DataFrame(data)
            
            if df.empty:
                raise ValueError(f"No data found in MongoDB collection: '{collection_name}' in database: '{database_name}'. "
                                 "Please ensure the collection is not empty before running the pipeline.")

            # El campo '_id' de MongoDB no es necesario para el entrenamiento del modelo.
            if '_id' in df.columns:
                df = df.drop(columns=['_id'])
            logger.info(f"Datos exportados de la colección {collection_name} en la base de datos {database_name}")
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        finally:
            # Asegurarse de que la conexión a la base de datos se cierre siempre.
            if client:
                client.close()
        
    def export_data_into_feature_store(self, df: pd.DataFrame) -> str:
        try:
            os.makedirs(self.data_ingestion_config.feature_store_dir, exist_ok=True)
            feature_store_file_path = os.path.join(self.data_ingestion_config.feature_store_dir, FILE_NAME)
            df.to_csv(feature_store_file_path, index=False)
            logger.info(f"Datos guardados en el feature store: {feature_store_file_path}")
            return feature_store_file_path
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def split_data_as_train_test(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            train_df, test_df = train_test_split(df, test_size=DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO, random_state=42)
            logger.info(f"Datos divididos en conjuntos de entrenamiento y prueba con una proporción de {DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO}")
            return train_df, test_df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe(
                collection_name=DATA_INGESTION_COLECTION_NAME, 
                database_name=DATA_INGESTION_DATABASE_NAME
            )
            # Se llama al método para guardar los datos, pero su valor de retorno no es necesario aquí.
            # El linter podría marcar 'feature_store_file_path' como una variable no utilizada.
            self.export_data_into_feature_store(dataframe)
            train_df, test_df = self.split_data_as_train_test(dataframe)
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.train_file_path,
                test_file_path=self.data_ingestion_config.test_file_path
            )
            os.makedirs(self.data_ingestion_config.ingested_dir, exist_ok=True)
            train_df.to_csv(self.data_ingestion_config.train_file_path, index=False)
            test_df.to_csv(self.data_ingestion_config.test_file_path, index=False)
            logger.info(f"Datos de entrenamiento guardados en: {self.data_ingestion_config.train_file_path}")
            logger.info(f"Datos de prueba guardados en: {self.data_ingestion_config.test_file_path}")
            return data_ingestion_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e


      
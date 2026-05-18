import os
import sys
import json
import pandas as pd
import pymongo

from dotenv import load_dotenv
# Las importaciones deben usar la ruta completa del paquete para que Python
# pueda encontrar los módulos correctamente.
# Además, el logger se exporta como 'logger', no 'logging'.
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger

# Cargar variables de entorno desde el archivo .env
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")


class NetworkDataExtract():
    def __init__(self):
        # El método __init__ estaba vacío, el bloque try-except no es necesario.
        pass

    def csv_to_json_convertor(self, file_path: str) -> list:
        """Lee un archivo CSV y lo convierte en una lista de diccionarios."""
        try:
            df = pd.read_csv(file_path)
            # La línea df.reset_index() es innecesaria aquí, ya que read_csv
            # crea un índice limpio y to_dict('records') no lo incluye por defecto.
            records = df.to_dict('records')
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def insert_data_mongodb(self, records: list, database_name: str, collection_name: str) -> int:
        """Inserta una lista de registros en una colección de MongoDB."""
        mongo_client = None
        try:
            # Usar variables locales es más limpio que asignar a atributos de instancia aquí.
            mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            database = mongo_client[database_name]
            collection = database[collection_name]
            collection.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        finally:
            if mongo_client:
                mongo_client.close()


if __name__ == '__main__':
    # Usar os.path.join para compatibilidad de rutas entre sistemas operativos
    FILE_PATH = os.path.join("Network_Data", "phisingData.csv")
    DATABASE = "KRISHAI"
    COLLECTION = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)
    logger.info(f"Se encontraron {len(records)} registros en el archivo CSV.")
    # Imprimir todos los registros puede ser muy verboso. Considera imprimir un resumen.
    # print(records)
    no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(f"Se insertaron {no_of_records} registros exitosamente.")

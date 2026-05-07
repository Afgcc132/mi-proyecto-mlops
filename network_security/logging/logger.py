import logging 
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Crear el directorio de logs basado en el directorio de trabajo actual
logs_path = os.path.join(os.getcwd(), LOG_DIR)
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO, 
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",       
    filemode="w"
)

# Create a logger instance that can be imported by other modules
logger = logging.getLogger("mlops_project_logger")

if __name__ == "__main__":
    logger.info("Logging has started")
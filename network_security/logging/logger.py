import logging 
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Es mejor definir la ruta de los logs de forma absoluta desde la raíz del proyecto
# en lugar de usar el directorio de trabajo actual (os.getcwd()).
# Esto asegura que los logs siempre se guarden en el mismo lugar, sin importar desde dónde se ejecute el script.
# Asumiendo que este archivo está en <project_root>/network_security/logging/logger.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
logs_path = os.path.join(PROJECT_ROOT, LOG_DIR)
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configuración dual: Archivo para local y Consola para AWS/Docker
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler() # Esto permite que los logs se vean en AWS CloudWatch/Docker logs
    ]
)

# Create a logger instance that can be imported by other modules
logger = logging.getLogger("mlops_project_logger")

if __name__ == "__main__":
    logger.info("Logging has started")
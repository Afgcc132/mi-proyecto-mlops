import sys
import os

import certifi
ca = certifi.where()

from dotenv import load_dotenv
load_dotenv()
mongodb_url = os.getenv("MONGO_DB_URL")

import pymongo
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger
from network_security.pipeline.training_pipeline import TrainingPipeline
from network_security.utils.ml_utils.model.estimator import NetworkModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Request
from uvicorn import run as app_run
from starlette.responses import RedirectResponse
import pandas as pd

from network_security.utils.main_utils.utils import load_object

from network_security.constant.training_pipeline import (
    DATA_INGESTION_COLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME
)

client = None
database = None
collection = None
if mongodb_url:
    client = pymongo.MongoClient(mongodb_url, tlsCAFile=ca)
    database = client[DATA_INGESTION_DATABASE_NAME]
    collection = database[DATA_INGESTION_COLECTION_NAME]

app = FastAPI()
origin = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")

# Cargamos el modelo y el preprocesador una sola vez al iniciar la aplicación.
# Esto optimiza el rendimiento y evita cargar archivos pesados en cada petición.
MODEL_DIR = os.getenv("MODEL_DIR", "final_model")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

try:
    logger.info(f"Cargando artefactos desde {MODEL_DIR}...")
    PREPROCESSOR = load_object(PREPROCESSOR_PATH)
    MODEL = load_object(MODEL_PATH)
    logger.info("Modelo y preprocesador cargados exitosamente.")
except Exception as e:
    logger.error(f"Error crítico: No se pudieron cargar los artefactos del modelo. Ruta: {MODEL_DIR}. Error: {e}")
    # En producción, podrías querer que la app falle aquí o use un modelo por defecto

NETWORK_MODEL_ESTIMATOR = NetworkModel(preprocessor=PREPROCESSOR, model=MODEL)

@app.get("/", tags=["auth"])
async def index(request: Request):
    return templates.TemplateResponse(request, "upload.html")

@app.get("/train")
async def train_route(background_tasks: BackgroundTasks):
    try:
        def run_training():
            train_pipeline = TrainingPipeline()
            train_pipeline.run_pipeline()
        
        background_tasks.add_task(run_training)
        return {"message": "Training pipeline started successfully in the background."}
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
@app.get("/predict")
async def predict_get_handler():
    # Si el usuario entra manualmente a /predict, lo devolvemos al inicio
    return RedirectResponse(url="/")

@app.post("/predict")
async def predict_route(request: Request,  file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)        
        # Usamos la instancia cargada globalmente
        y_pred = NETWORK_MODEL_ESTIMATOR.predict(df)
        df["prediction"] = y_pred
        
        # Aseguramos que la carpeta de salida exista y guardamos sin el índice
        os.makedirs("prediction_output", exist_ok=True)
        df.to_csv("prediction_output/output.csv", index=False)
        
        logger.info(f"Predicción completada. Registros procesados: {len(df)}")
        table_html = df.to_html(classes="table table-striped")
        return templates.TemplateResponse(request, "table.html", {"table_html": table_html})
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)


from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Es una buena práctica de seguridad cargar las credenciales desde variables de entorno
# en lugar de escribirlas directamente en el código.
uri = os.getenv("MONGO_DB_URL")
# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
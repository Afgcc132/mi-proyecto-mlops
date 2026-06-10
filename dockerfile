FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws /var/lib/apt/lists/*

COPY requirements.txt setup.py ./
COPY network_security ./network_security
COPY app.py ./
COPY push_data.py ./
COPY templates ./templates
COPY data_schema ./data_schema
COPY final_model ./final_model

# Instalamos los requerimientos y el proyecto como paquete local para habilitar los imports
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

RUN mkdir -p prediction_output logs

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

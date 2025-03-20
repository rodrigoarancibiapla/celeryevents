# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copia los archivos necesarios a la imagen
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Asegúrate de tener Celery en el requirements.txt
# En tu requirements.txt debe incluir:
# celery==X.X.X

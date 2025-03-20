FROM python:3.12-slim

WORKDIR /app

# Copia el archivo requirements.txt dentro del contenedor
COPY requirements.txt /app/requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la API al contenedor
COPY . /app/customersAPI

# Define el puerto que va a usar la API
EXPOSE 8002

# Comando para iniciar la API con uvicorn
CMD ["uvicorn", "transactionsAPI.api:app", "--host", "0.0.0.0", "--port", "8002"]

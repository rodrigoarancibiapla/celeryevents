import io
from celery import Celery
import os
import pandas as pd
import requests
import boto3
from botocore.client import Config

url_api_customers = os.getenv("URL_API_CUSTOMERS")
url_api_transactions = os.getenv("URL_API_TRANSACTIONS")
LOCALSTACK_ENDPOINT_URL = "http://" + os.getenv("LOCALSTACK_HOST") + ":4566"  # URL de LocalStack
BUCKET_NAME = "files"  # Nombre del bucket S3

# Configura el cliente de S3 para LocalStack
s3_client = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT_URL,
    aws_access_key_id="test",  # Credenciales de prueba (LocalStack no requiere credenciales reales)
    aws_secret_access_key="test",
    config=Config(signature_version="s3v4"),
)

# Configuración de Celery con Redis
redis_host = os.getenv('REDIS_HOST', 'redis')  # Cambiar si Redis está en otro servidor
broker = f'redis://{redis_host}:6379/0'
backend = f'redis://{redis_host}:6379/0'

app = Celery('tasks', broker=broker, backend=backend)



@app.task
def generar_clientes():
    print("generar_clientes")
    
    # Nombre del archivo que se subirá al bucket
    clientes_file = "clientes.csv"
    
    # Crear el archivo CSV en memoria
    csv_buffer = []
    csv_buffer.append(["cliente_id", "nombre", "email"])
    
    # Obtener datos de la API
    response = requests.get(url_api_customers + "/clientes")
    result_clientes = response.json()
    
    for row in result_clientes:
        csv_buffer.append([row["cliente_id"], row["nombre"], row["email"]])
    
    # Convertir la lista a un archivo CSV en memoria
    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])
    
    # Subir el archivo al bucket S3
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=clientes_file,
            Body=csv_data,
        )
        print(f"✔ Archivo subido a S3: s3://{BUCKET_NAME}/{clientes_file}")
    except Exception as e:
        print(f"❌ Error al subir el archivo a S3: {e}")
    

    """ Genera un archivo clientes.csv """
    return clientes_file # Devuelve la ruta para la siguiente tarea


@app.task
def generar_transacciones(clientes_file):
    print("generar_transacciones")
    
    # Nombre del archivo que se subirá al bucket
    transacciones_file = "transacciones.csv"
    
    # Crear el archivo CSV en memoria
    csv_buffer = []
    csv_buffer.append(["transaccion_id", "cliente_id", "monto", "fecha"])
    
    # Obtener datos de la API
    response = requests.get(url_api_transactions + "/transacciones")
    result_transacciones = response.json()
    
    for row in result_transacciones:
        csv_buffer.append([row["transaccion_id"], row["cliente_id"], row["monto"], row["fecha"]])
    
    # Convertir la lista a un archivo CSV en memoria
    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])
    
    # Subir el archivo al bucket S3
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=transacciones_file,
            Body=csv_data,
        )
        print(f"✔ Archivo subido a S3: s3://{BUCKET_NAME}/{transacciones_file}")
    except Exception as e:
        print(f"❌ Error al subir el archivo a S3: {e}")
    
    """ Genera transacciones.csv basado en clientes """
    
    return clientes_file, transacciones_file  # Devuelve ambos archivos
    
@app.task
def consolidar_datos(data):
    clientes_file, transacciones_file = data

    # 1. Leer archivo clientes.csv desde S3
    try:
        print("BUCKET_NAME","--",clientes_file)
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=clientes_file)
        df_clientes = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ Archivo {clientes_file} leído desde S3")
    except Exception as e:
        print(f"❌ Error al leer {clientes_file} desde S3: {e}")
        return None

    # 2. Leer archivo transacciones.csv desde S3
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=transacciones_file)
        df_transacciones = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ Archivo {transacciones_file} leído desde S3")
    except Exception as e:
        print(f"❌ Error al leer {transacciones_file} desde S3: {e}")
        return None

    # 3. Consolidar los datos
    df_consolidado = df_transacciones.merge(df_clientes, on="cliente_id", how="left")

    # 4. Guardar el archivo consolidado en S3
    consolidacion_file = "consolidacion.csv"
    try:
        # Convertir el DataFrame a CSV en memoria
        csv_buffer = io.StringIO()
        df_consolidado.to_csv(csv_buffer, index=False)
        
        # Subir el archivo a S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=consolidacion_file,
            Body=csv_buffer.getvalue(),
        )
        print(f"✔ Archivo consolidado subido a S3: s3://{BUCKET_NAME}/{consolidacion_file}")
    except Exception as e:
        print(f"❌ Error al subir {consolidacion_file} a S3: {e}")
        return None

    return consolidacion_file

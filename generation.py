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
BUCKET_NAME = "files"  # Name del bucket S3

# Configura el Customer de S3 para LocalStack
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
def generar_Customers():
    print("generar_Customers")
    
    # Name del archivo que se subirá al bucket
    Customers_file = "Customers.csv"
    
    # Crear el archivo CSV en memoria
    csv_buffer = []
    csv_buffer.append(["Customer_id", "name", "email"])
    
    # Obtener datos de la API
    response = requests.get(url_api_customers + "/Customers")
    result_Customers = response.json()
    
    for row in result_Customers:
        csv_buffer.append([row["Customer_id"], row["name"], row["email"]])
    
    # Convertir la lista a un archivo CSV en memoria
    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])
    
    # Subir el archivo al bucket S3
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=Customers_file,
            Body=csv_data,
        )
        print(f"✔ Archivo subido a S3: s3://{BUCKET_NAME}/{Customers_file}")
    except Exception as e:
        print(f"❌ Error al subir el archivo a S3: {e}")
    

    """ Genera un archivo Customers.csv """
    return Customers_file # Devuelve la ruta para la siguiente tarea


@app.task
def generar_transactions(Customers_file):
    print("generar_transactions")
    
    # Name del archivo que se subirá al bucket
    transactions_file = "transactions.csv"
    
    # Crear el archivo CSV en memoria
    csv_buffer = []
    csv_buffer.append(["transaction_id", "Customer_id", "amount", "date"])
    
    # Obtener datos de la API
    response = requests.get(url_api_transactions + "/transactions")
    result_transactions = response.json()
    
    for row in result_transactions:
        csv_buffer.append([row["transaction_id"], row["Customer_id"], row["amount"], row["date"]])
    
    # Convertir la lista a un archivo CSV en memoria
    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])
    
    # Subir el archivo al bucket S3
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=transactions_file,
            Body=csv_data,
        )
        print(f"✔ Archivo subido a S3: s3://{BUCKET_NAME}/{transactions_file}")
    except Exception as e:
        print(f"❌ Error al subir el archivo a S3: {e}")
    
    """ Genera transactions.csv basado en Customers """
    
    return Customers_file, transactions_file  # Devuelve ambos archivos
    
@app.task
def consolidar_datos(data):
    Customers_file, transactions_file = data

    # 1. Leer archivo Customers.csv desde S3
    try:
        print("BUCKET_NAME","--",Customers_file)
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=Customers_file)
        df_Customers = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ Archivo {Customers_file} leído desde S3")
    except Exception as e:
        print(f"❌ Error al leer {Customers_file} desde S3: {e}")
        return None

    # 2. Leer archivo transactions.csv desde S3
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=transactions_file)
        df_transactions = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ Archivo {transactions_file} leído desde S3")
    except Exception as e:
        print(f"❌ Error al leer {transactions_file} desde S3: {e}")
        return None

    # 3. Consolidar los datos
    df_consolidado = df_transactions.merge(df_Customers, on="Customer_id", how="left")

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

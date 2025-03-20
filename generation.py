from celery import Celery, chain
import os
import pandas as pd
import csv
import requests
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

url_api_customers = os.getenv("URL_API_CUSTOMERS")
url_api_transactions = os.getenv("URL_API_TRANSACTIONS")

# Configuración de Celery con Redis
redis_host = os.getenv('REDIS_HOST', 'redis')  # Cambiar si Redis está en otro servidor
broker = f'redis://{redis_host}:6379/0'
backend = f'redis://{redis_host}:6379/0'

app = Celery('tasks', broker=broker, backend=backend)

# Directorio donde se guardarán los CSVs
OUTPUT_DIR = "./data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.task
def generar_clientes():
    print("generar_clientes")
    clientes_file = os.path.join(OUTPUT_DIR, "clientes.csv")
    with open(clientes_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["cliente_id", "nombre", "email"])
        response = requests.get(url_api_customers + "/clientes")
        result_clientes = response.json()
            
        for row in result_clientes:
            writer.writerow([row["cliente_id"], row["nombre"], row["email"]])
    print(f"✔ Archivo generado: {clientes_file}")
    

    """ Genera un archivo clientes.csv """
    return clientes_file  # Devuelve la ruta para la siguiente tarea


@app.task
def generar_transacciones(clientes_file):
    print("generar_transacciones")
    transacciones_file = os.path.join(OUTPUT_DIR, "transacciones.csv")
    with open(transacciones_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["transaccion_id", "cliente_id", "monto", "fecha"])
        response = requests.get(url_api_transactions + "/transacciones")
        result_transacciones = response.json()
        for row in result_transacciones:
            writer.writerow([row['transaccion_id'], row['cliente_id'], row['monto'], row['fecha']])
    print(f"✔ Archivo generado: {transacciones_file}")
   
    """ Genera transacciones.csv basado en clientes """
    
    return clientes_file, transacciones_file  # Devuelve ambos archivos


@app.task
def consolidar_archivos(data):
    print("consolidar_archivos")
    """ Junta clientes.csv y transacciones.csv en consolidacion.csv """
    clientes_file, transacciones_file = data

    df_clientes = pd.read_csv(clientes_file)
    df_transacciones = pd.read_csv(transacciones_file)

    df_consolidado = df_transacciones.merge(df_clientes, on="cliente_id", how="left")

    consolidacion_file = os.path.join(OUTPUT_DIR, "consolidacion.csv")
    df_consolidado.to_csv(consolidacion_file, index=False)

    print(f"✔ Archivo consolidado generado: {consolidacion_file}")
    return consolidacion_file


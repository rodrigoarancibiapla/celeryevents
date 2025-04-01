import io
from celery import Celery
import os
import pandas as pd
import requests
import boto3
from botocore.client import Config

url_api_customers = os.getenv("URL_API_CUSTOMERS")
url_api_transactions = os.getenv("URL_API_TRANSACTIONS")
LOCALSTACK_ENDPOINT_URL = "http://" + os.getenv("LOCALSTACK_HOST") + ":4566"
BUCKET_NAME = "files"

s3_client = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT_URL,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    config=Config(signature_version="s3v4"),
)

redis_host = os.getenv('REDIS_HOST', 'redis')
broker = f'redis://{redis_host}:6379/0'
backend = f'redis://{redis_host}:6379/0'

app = Celery('tasks', broker=broker, backend=backend)


@app.task
def generate_customers():

    Customers_file = "customers.csv"

    csv_buffer = []
    csv_buffer.append(["customer_id", "name", "email"])

    response = requests.get(url_api_customers + "/Customers")
    result_Customers = response.json()

    for row in result_Customers:
        csv_buffer.append([row["customer_id"], row["name"], row["email"]])

    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=Customers_file,
            Body=csv_data,
        )
        print(f"✔ File uploaded to  S3: s3://{BUCKET_NAME}/{Customers_file}")
    except Exception as e:
        print(f"❌ Error uploading file to S3: {e}")

    return Customers_file


@app.task
def generate_transactions(Customers_file):

    transactions_file = "transactions.csv"

    csv_buffer = []
    csv_buffer.append(["transaction_id", "customer_id", "amount", "date"])

    response = requests.get(url_api_transactions + "/transactions")
    result_transactions = response.json()

    for row in result_transactions:
        csv_buffer.append([row["transaction_id"], row["customer_id"], row["amount"], row["date"]])

    csv_data = "\n".join([",".join(map(str, row)) for row in csv_buffer])

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=transactions_file,
            Body=csv_data,
        )
        print(f"✔ File uploaded to S3: s3://{BUCKET_NAME}/{transactions_file}")
    except Exception as e:
        print(f"❌ Error uploading file to S3: {e}")

    return Customers_file, transactions_file  #


@app.task
def consolidate_data(data):
    Customers_file, transactions_file = data

    try:
        print("BUCKET_NAME", "--", Customers_file)
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=Customers_file)
        df_Customers = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ Filed  {Customers_file} read")
    except Exception as e:
        print(f"❌ Error reading  {Customers_file}: {e}")
        return None

    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=transactions_file)
        df_transactions = pd.read_csv(io.BytesIO(response["Body"].read()))
        print(f"✔ File {transactions_file} read")
    except Exception as e:
        print(f"❌ Error reading {transactions_file}: {e}")
        return None

    df_consolidado = df_transactions.merge(df_Customers, on="customer_id", how="left")
    consolidation_file = "consolidation.csv"
    try:

        csv_buffer = io.StringIO()
        df_consolidado.to_csv(csv_buffer, index=False)

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=consolidation_file,
            Body=csv_buffer.getvalue(),
        )
        print(f"✔ Consolidat file uploaded to S3: s3://{BUCKET_NAME}/{consolidation_file}")
    except Exception as e:
        print(f"❌ Error uploading {consolidation_file}: {e}")
        return None

    return consolidation_file

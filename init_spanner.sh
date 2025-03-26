#!/bin/bash

# Obtener la IP del servicio spanner_emulator
SPANNER_IP=$(getent hosts spanner_emulator | awk '{ print $1 }')
echo "IP de spanner_emulator: $SPANNER_IP"

# Configurar gcloud para usar el emulador
gcloud config set auth/disable_credentials true
gcloud config set project my-project
gcloud config set api_endpoint_overrides/spanner http://$SPANNER_IP:9020/ --quiet

# Autenticar con credenciales falsas
echo '{"type": "authorized_user"}' > /tmp/fake_creds.json
gcloud auth activate-service-account --key-file=/tmp/fake_creds.json

# Esperar a que el emulador de Spanner esté listo
echo "Esperando 10 segundos para que el emulador esté listo..."
sleep 10

# Crear la instancia de Spanner
echo "Creando instancia de Spanner..."
gcloud spanner instances create test-instance \
  --config=emulator-config \
  --description="Test Instance" \
  --nodes=1

# Crear la base de datos
echo "Creando base de datos..."
gcloud spanner databases create test-db \
  --instance=test-instance

# Crear las tablas
echo "Creando las tablas..."
gcloud spanner databases ddl update test-db \
  --instance=test-instance \
  --ddl="
CREATE TABLE customers (
  customer_id INT64 NOT NULL,
  name STRING(100),
  email STRING(100)
) PRIMARY KEY(customer_id);
"

gcloud spanner databases ddl update test-db \
  --instance=test-instance \
  --ddl="
CREATE TABLE transactions (
  transaction_id INT64 NOT NULL,
  customer_id INT64 NOT NULL,
  amount FLOAT64 NOT NULL,
  date DATE NOT NULL
) PRIMARY KEY(transaction_id);
"

# Insertar 10 customers de prueba
echo "Insertando 10 customers de prueba..."
for i in {1..10}; do
  customer_id=$i
  name="Customer $i"
  email="customer$i@example.com"

  gcloud spanner rows insert --database=test-db --instance=test-instance --table=customers \
    --data="customer_id=$customer_id,name='$name',email='$email'"
done

# Insertar 30 transactions de prueba
echo "Insertando 30 transactions de prueba..."
for i in {1..30}; do
  transaction_id=$i
  customer_id=$(( (RANDOM % 10) + 1 ))  # Asignar a un customer aleatorio (1-10)
  amount=$(awk -v min=10 -v max=1000 'BEGIN{srand(); print int(min+rand()*(max-min+1))}')  # Monto aleatorio entre 10 y 1000

  
  # Generar una date aleatoria en el formato YYYY-MM-DD
  year=$(( (RANDOM % 3) + 2021 ))  # Año entre 2021 y 2023
  month=$(( (RANDOM % 12) + 1 ))   # Mes entre 1 y 12
  day=$(( (RANDOM % 28) + 1 ))     # Día entre 1 y 28 (para evitar problemas con meses de 30/31 días)
  date=$(printf "%04d-%02d-%02d" $year $month $day)  # Formatear como YYYY-MM-DD

  gcloud spanner rows insert --database=test-db --instance=test-instance --table=transactions \
    --data="transaction_id=$transaction_id,customer_id=$customer_id,amount=$amount,date=$date"
done

echo "Spanner initialization complete!"
#!/bin/sh

# Espera por customers_api
while ! nc -z customers_api 8001; do 
  echo "Waiting for customers_api..."
  sleep 2
done

# Espera por transactions_api
while ! nc -z transactions_api 8002; do 
  echo "Waiting for transactions_api..."
  sleep 2
done

echo "All files are ready!"
exec "$@"
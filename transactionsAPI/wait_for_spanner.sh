#!/bin/bash
echo "🔍 Verificando que Spanner tenga las 30 transacciones..."

# Configuración de Cloud SDK para el emulador

SPANNER_IP=$(getent hosts spanner_emulator | awk '{ print $1 }')
echo "IP de spanner_emulator: $SPANNER_IP"

# Configurar gcloud para usar el emulador
gcloud config set auth/disable_credentials true
gcloud config set project my-project
gcloud config set api_endpoint_overrides/spanner http://$SPANNER_IP:9020/ --quiet

ATTEMPTS=0
MAX_ATTEMPTS=24  # 24 intentos × 5 segundos = 120 segundos máximo
SUCCESS=false

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ] && [ "$SUCCESS" = false ]; do
  COUNT=$(gcloud spanner databases execute-sql test-db \
  --instance=test-instance \
  --sql="SELECT COUNT(*) as total FROM transactions" | 
  tail -n 1 | 
  awk '{print $NF}')
  if [ "$COUNT" -eq 30 ]; then
    SUCCESS=true
    echo "✅ Spanner listo con 30 transacciones registradas"
  else
    ATTEMPTS=$((ATTEMPTS+1))
    echo "⏳ Intento $ATTEMPTS/$MAX_ATTEMPTS - Transacciones encontradas: $COUNT/30. Reintentando en 5s..."
    sleep 5
  fi
done

if [ "$SUCCESS" = false ]; then
  echo "⚠️  Advertencia: No se encontraron 30 transacciones después de $MAX_ATTEMPTS intentos"
  echo "Continuando con la ejecución, pero la base de datos puede no estar completamente inicializada"
fi

exec "$@"
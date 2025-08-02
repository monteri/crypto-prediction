#!/bin/sh

echo "🌟 Starting Kafka and ksqlDB bootstrap process..."

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
while ! nc -z kafka1 19092; do
  echo "Waiting for Kafka..."
  sleep 2
done
echo "✅ Kafka is ready"

# Wait for ksqlDB to be ready
echo "⏳ Waiting for ksqlDB to be ready..."
retry_count=0
max_retries=10
while ! curl -f http://ksqldb-server:8088/info > /dev/null 2>&1; do
  retry_count=$((retry_count + 1))
  if [ $retry_count -ge $max_retries ]; then
    echo "❌ ksqlDB failed to start after $max_retries attempts"
    exit 1
  fi
  echo "Waiting for ksqlDB... (attempt $retry_count/$max_retries)"
  sleep 2
done
echo "✅ ksqlDB is ready"

# Run the bootstrap from the bootstrap directory
echo "🚀 Running bootstrap..."
cd bootstrap
python bootstrap_complete.py

echo "✅ Bootstrap completed!"
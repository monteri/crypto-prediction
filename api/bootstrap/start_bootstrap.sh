#!/bin/bash

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
while ! curl -f http://ksqldb-server:8088/info > /dev/null 2>&1; do
  echo "Waiting for ksqlDB..."
  sleep 2
done
echo "✅ ksqlDB is ready"

# Run the bootstrap from the bootstrap directory
echo "🚀 Running bootstrap..."
cd bootstrap
python bootstrap_complete.py

echo "✅ Bootstrap completed!"
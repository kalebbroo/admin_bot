#!/bin/bash
echo "Building Docker image..."
docker build -t admin_bot .
echo "Running Docker Compose..."
docker-compose up
read -p "Press Enter to exit"
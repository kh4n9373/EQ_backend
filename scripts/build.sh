#!/bin/bash

echo "Building Docker image..."
docker build -t eq-test-backend .
echo "Build completed!"
#!/bin/bash

# Apply ConfigMap and Secret
echo "Applying ConfigMap and Secret..."
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml

# Apply MySQL Deployment and Service
echo "Deploying MySQL..."
kubectl apply -f kubernetes/db/

# Apply User-Management Deployment and Service
echo "Deploying User-Management Microservice..."
kubectl apply -f kubernetes/user-management/

# Apply Frontend Deployment and Service
echo "Deploying Frontend Microservice..."
kubectl apply -f kubernetes/frontend/
echo "Deployment complete!"

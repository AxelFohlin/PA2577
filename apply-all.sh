#!/bin/bash

# Apply ConfigMap and Secret
echo "Applying ConfigMap and Secret..."
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml

# Apply Persistent Volume (if used)
echo "Applying Persistent Volume..."
kubectl apply -f kubernetes/db/mysql-pv.yaml

# Apply MySQL Deployment and Service
echo "Deploying MySQL..."
kubectl apply -f kubernetes/db/deployment.yaml
kubectl apply -f kubernetes/db/service.yaml

# Apply User-Management Deployment and Service
echo "Deploying User-Management Microservice..."
kubectl apply -f kubernetes/user-management/deployment.yaml
kubectl apply -f kubernetes/user-management/service.yaml

# Apply Frontend Deployment and Service
echo "Deploying Frontend Microservice..."
kubectl apply -f kubernetes/frontend/deployment.yaml
kubectl apply -f kubernetes/frontend/service.yaml

echo "Deployment complete!"

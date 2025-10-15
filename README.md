# Dice App Deployment on Minikube with Podman

This project deploys a Flask dice rolling application to a local Minikube cluster running on Podman, complete with monitoring via Prometheus and Grafana.

## Prerequisites

- Minikube with Podman driver
- kubectl
- Helm 3

## Deployment Steps

### 1. Build the Docker Image

```bash
# Build the image using Podman
podman build -t dice-app:latest .

# Load the image into Minikube
podman save dice-app:latest -o dice-app.tar
minikube image load dice-app.tar
```

### 2. Enable Ingress

```bash
minikube addons enable ingress
```

### 3. Deploy the Application

```bash
# Deploy the application with sidecar log streamer
kubectl apply -f deployment.yaml

# Create the service
kubectl apply -f service.yaml

# Create the ingress
kubectl apply -f ingress.yaml
```

### 4. Install Prometheus and Grafana

```bash
# Add the Prometheus community Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack with custom values
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f prometheus-values.yaml \
  --namespace monitoring \
  --create-namespace
```

### 5. Import Grafana Dashboard

```bash
kubectl apply -f dashboard-configmap.yaml
```

### 6. Access the Application

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) dice-app.local" | sudo tee -a /etc/hosts

# Access the application
curl http://dice-app.local/dice
curl http://dice-app.local/health
```

## Viewing Logs

View logs from the main container:
```bash
kubectl logs -f deployment/dice-app -c dice-app
```

View logs from the log-streamer sidecar:
```bash
kubectl logs -f deployment/dice-app -c log-streamer
```

## Accessing Grafana

```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open http://localhost:3000
# Default credentials: admin / admin
```

## Accessing Prometheus

```bash
# Port-forward Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open http://localhost:9090
```

## Cleanup

```bash
kubectl delete -f deployment.yaml
kubectl delete -f service.yaml
kubectl delete -f ingress.yaml
kubectl delete -f dashboard-configmap.yaml
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```

## Features

- **Health Probes**: Liveness and readiness probes using `/health` endpoint
- **Log Streaming**: Sidecar container streaming logs in real-time using `tail -f`
- **Ingress**: External access via `dice-app.local`
- **Monitoring**: Kubernetes metrics via kube-state-metrics and cAdvisor
- **Dashboard Panels**:
  - Application Status (Running/Down based on pod phase)
  - Pod Status over time
  - CPU Usage gauge (percentage)
  - Memory Usage gauge (percentage)
  - Total Pods count
  - Container Restarts count
  - Memory Usage over time (bytes)
  - CPU Usage over time (percentage)

## Notes

- The application's `/health` endpoint returns JSON which cannot be scraped by Prometheus directly
- The dashboard uses kube-state-metrics and cAdvisor metrics instead (included with kube-prometheus-stack)
- All monitoring data comes from Kubernetes cluster metrics
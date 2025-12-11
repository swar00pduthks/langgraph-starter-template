# Azure Integration Guide

This guide covers integrating the LangGraph Starter Template with various Azure services.

## Overview

The template is designed to work seamlessly with Azure services:

- **Azure Kubernetes Service (AKS)**: Container orchestration
- **Azure Container Registry (ACR)**: Docker image storage
- **Azure Key Vault**: Secret management
- **Azure Monitor**: Logging and monitoring
- **Application Insights**: Application performance monitoring
- **Azure Front Door**: Global CDN and load balancing (optional)

## Azure Key Vault Integration

### Setup

1. **Create Key Vault**

```bash
az keyvault create \
  --name <your-keyvault-name> \
  --resource-group <your-resource-group> \
  --location <location>
```

2. **Add Secrets**

```bash
# Add OpenAI API key
az keyvault secret set \
  --vault-name <your-keyvault-name> \
  --name "openai-api-key" \
  --value "<your-openai-key>"

# Add A2A secret key
az keyvault secret set \
  --vault-name <your-keyvault-name> \
  --name "a2a-secret-key" \
  --value "<your-secret>"

# Add Application Insights connection string
az keyvault secret set \
  --vault-name <your-keyvault-name> \
  --name "appinsights-connection-string" \
  --value "<your-connection-string>"
```

### Access from AKS

#### Option 1: Using Managed Identity (Recommended)

1. **Enable managed identity for AKS**

```bash
az aks update \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --enable-managed-identity
```

2. **Grant Key Vault access**

```bash
# Get the managed identity
IDENTITY_CLIENT_ID=$(az aks show \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --query identityProfile.kubeletidentity.clientId -o tsv)

# Grant access to Key Vault
az keyvault set-policy \
  --name <keyvault-name> \
  --object-id $IDENTITY_CLIENT_ID \
  --secret-permissions get list
```

3. **Install CSI Secret Store Driver**

```bash
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name <cluster-name> \
  --resource-group <resource-group>
```

4. **Create SecretProviderClass**

```yaml
# keyvault-secrets.yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: langgraph-secrets
  namespace: production
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "<your-identity-client-id>"
    keyvaultName: "<your-keyvault-name>"
    tenantId: "<your-tenant-id>"
    objects: |
      array:
        - |
          objectName: openai-api-key
          objectType: secret
          objectVersion: ""
        - |
          objectName: a2a-secret-key
          objectType: secret
          objectVersion: ""
        - |
          objectName: appinsights-connection-string
          objectType: secret
          objectVersion: ""
  secretObjects:
  - secretName: langgraph-secrets
    type: Opaque
    data:
    - objectName: openai-api-key
      key: openai-api-key
    - objectName: a2a-secret-key
      key: a2a-secret-key
    - objectName: appinsights-connection-string
      key: appinsights-connection-string
```

Apply it:
```bash
kubectl apply -f keyvault-secrets.yaml
```

5. **Update Deployment to use secrets**

The Helm chart is already configured to use these secrets via the `values.yaml` file.

#### Option 2: Using Service Principal

1. **Create service principal**

```bash
az ad sp create-for-rbac --name langgraph-sp
```

2. **Grant Key Vault access**

```bash
az keyvault set-policy \
  --name <keyvault-name> \
  --spn <service-principal-app-id> \
  --secret-permissions get list
```

3. **Create Kubernetes secret**

```bash
kubectl create secret generic azure-credentials \
  --from-literal=client-id=<sp-app-id> \
  --from-literal=client-secret=<sp-password> \
  --namespace production
```

### Access from Application Code

The application automatically reads secrets from environment variables. No code changes needed.

```python
from app.core.config import get_settings

settings = get_settings()
openai_key = settings.openai_api_key  # Loaded from env var
```

---

## Azure Monitor & Application Insights

### Setup Application Insights

1. **Create Application Insights resource**

```bash
az monitor app-insights component create \
  --app langgraph-app-insights \
  --location <location> \
  --resource-group <resource-group> \
  --application-type web
```

2. **Get connection string**

```bash
az monitor app-insights component show \
  --app langgraph-app-insights \
  --resource-group <resource-group> \
  --query connectionString -o tsv
```

3. **Add to Key Vault or Kubernetes secret**

```bash
az keyvault secret set \
  --vault-name <keyvault-name> \
  --name "appinsights-connection-string" \
  --value "<connection-string>"
```

### Enable Monitoring in Application

Update `.env` or Helm values:

```yaml
env:
  - name: ENABLE_MONITORING
    value: "true"

secrets:
  - name: APPLICATIONINSIGHTS_CONNECTION_STRING
    secretName: langgraph-secrets
    secretKey: appinsights-connection-string
```

### View Telemetry

The application uses OpenTelemetry to send:
- **Traces**: Request/response traces
- **Metrics**: Performance metrics
- **Logs**: Application logs

Access in Azure Portal:
1. Navigate to Application Insights resource
2. View in the **Application Map**, **Live Metrics**, and **Logs** sections

---

## Azure Container Registry (ACR)

### Setup

1. **Create ACR**

```bash
az acr create \
  --resource-group <resource-group> \
  --name <acr-name> \
  --sku Standard
```

2. **Login to ACR**

```bash
az acr login --name <acr-name>
```

3. **Attach ACR to AKS**

```bash
az aks update \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --attach-acr <acr-name>
```

### Build and Push Images

```bash
# Build
docker build -t <acr-name>.azurecr.io/langgraph-app:v1.0.0 .

# Push
docker push <acr-name>.azurecr.io/langgraph-app:v1.0.0
```

### Use in Kubernetes

Update Helm values:

```yaml
image:
  repository: <acr-name>.azurecr.io/langgraph-app
  tag: "v1.0.0"
```

---

## Azure Monitor for Containers

### Enable Container Insights

```bash
az aks enable-addons \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --addons monitoring
```

### View Container Logs

1. Navigate to AKS resource in Azure Portal
2. Go to **Insights** → **Containers**
3. View logs, metrics, and performance data

### Query Logs with KQL

Example Kusto queries:

```kql
// View application logs
ContainerLog
| where ContainerName == "langgraph-app"
| order by TimeGenerated desc
| limit 100

// View error logs
ContainerLog
| where ContainerName == "langgraph-app"
| where LogEntry contains "ERROR"
| order by TimeGenerated desc

// View pod metrics
Perf
| where ObjectName == "K8SContainer"
| where CounterName == "cpuUsageNanoCores"
| summarize avg(CounterValue) by bin(TimeGenerated, 5m), InstanceName
```

---

## Azure Front Door (Optional)

For global distribution and CDN:

1. **Create Azure Front Door**

```bash
az afd profile create \
  --profile-name langgraph-frontdoor \
  --resource-group <resource-group> \
  --sku Standard_AzureFrontDoor
```

2. **Add endpoint**

```bash
az afd endpoint create \
  --endpoint-name langgraph-endpoint \
  --profile-name langgraph-frontdoor \
  --resource-group <resource-group>
```

3. **Configure origin**

```bash
az afd origin-group create \
  --origin-group-name langgraph-origin-group \
  --profile-name langgraph-frontdoor \
  --resource-group <resource-group>

az afd origin create \
  --origin-name langgraph-aks \
  --origin-group-name langgraph-origin-group \
  --profile-name langgraph-frontdoor \
  --resource-group <resource-group> \
  --host-name <your-ingress-ip-or-domain>
```

---

## Azure Active Directory (AAD) Integration

For authentication:

1. **Register application in AAD**

```bash
az ad app create --display-name langgraph-app
```

2. **Configure OAuth2 endpoints**

Add to FastAPI application:

```python
from fastapi import Depends, Security
from fastapi.security import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
)

@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Validate token
    return {"message": "Authenticated"}
```

---

## Cost Optimization

### Right-size Resources

```yaml
# Helm values
resources:
  requests:
    cpu: 250m      # Start small
    memory: 256Mi
  limits:
    cpu: 1000m
    memory: 1Gi

autoscaling:
  minReplicas: 2   # Minimum for HA
  maxReplicas: 10  # Adjust based on load
```

### Use Reserved Instances

For production workloads, consider:
- Reserved VM instances for AKS nodes
- Reserved capacity for Azure resources

### Monitor Costs

```bash
# View cost analysis
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

---

## Security Best Practices

1. **Use Managed Identities**: Avoid storing credentials
2. **Enable RBAC**: Role-based access control for AKS
3. **Network Policies**: Restrict pod-to-pod communication
4. **Private Endpoints**: Use private endpoints for Key Vault, ACR
5. **Azure Policy**: Enforce security policies
6. **Vulnerability Scanning**: Enable in ACR

---

## Troubleshooting

### Key Vault Access Issues

```bash
# Verify access policy
az keyvault show --name <keyvault-name> --query properties.accessPolicies

# Test secret access
az keyvault secret show --name openai-api-key --vault-name <keyvault-name>
```

### Container Registry Issues

```bash
# Verify ACR integration
az aks check-acr \
  --resource-group <resource-group> \
  --name <cluster-name> \
  --acr <acr-name>.azurecr.io
```

### Application Insights Not Receiving Data

1. Verify connection string is correct
2. Check application logs for errors
3. Ensure `ENABLE_MONITORING=true`
4. Verify network connectivity from AKS to Application Insights

---

## Next Steps

- [AKS Deployment Guide](aks-deployment.md)
- [Architecture Overview](architecture.md)
- [Getting Started](getting-started.md)

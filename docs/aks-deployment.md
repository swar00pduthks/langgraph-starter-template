# Deploying to Azure Kubernetes Service (AKS)

This guide walks you through deploying the LangGraph Starter Template to Azure Kubernetes Service.

## Prerequisites

- Azure CLI installed and configured
- kubectl installed
- Helm 3.x installed
- An Azure subscription
- Docker image built and pushed to a container registry

## Step 1: Set Up Azure Resources

### Create Resource Group

```bash
# Set variables
export RESOURCE_GROUP="langgraph-rg"
export LOCATION="eastus"
export AKS_CLUSTER="langgraph-aks"
export ACR_NAME="langgraphacr"  # Must be globally unique

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### Create Azure Container Registry (ACR)

```bash
# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard

# Login to ACR
az acr login --name $ACR_NAME
```

### Create AKS Cluster

```bash
# Create AKS cluster with ACR integration
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --attach-acr $ACR_NAME \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
```

## Step 2: Set Up Azure Key Vault

```bash
# Create Key Vault
export KEYVAULT_NAME="langgraph-kv"  # Must be globally unique

az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Add secrets
az keyvault secret set --vault-name $KEYVAULT_NAME --name "openai-api-key" --value "your-openai-key"
az keyvault secret set --vault-name $KEYVAULT_NAME --name "a2a-secret-key" --value "your-a2a-secret"

# Enable Key Vault integration with AKS (using CSI driver)
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name $AKS_CLUSTER \
  --resource-group $RESOURCE_GROUP
```

## Step 3: Build and Push Docker Image

```bash
# Build the image
docker build -t $ACR_NAME.azurecr.io/langgraph-app:latest .

# Push to ACR
docker push $ACR_NAME.azurecr.io/langgraph-app:latest
```

## Step 4: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace production

# Create secrets from Key Vault (or directly)
kubectl create secret generic langgraph-secrets \
  --from-literal=openai-api-key="your-openai-key" \
  --from-literal=a2a-secret-key="your-a2a-secret" \
  --from-literal=appinsights-connection-string="your-connection-string" \
  --namespace production
```

### Alternative: Use Azure Key Vault CSI Driver

Create a `SecretProviderClass`:

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
    tenantId: "<your-tenant-id>"
```

Apply it:
```bash
kubectl apply -f keyvault-secrets.yaml
```

## Step 5: Deploy with Helm

### Update Helm Values

Edit `helm/langgraph-app/values.yaml`:

```yaml
image:
  repository: langgraphacr.azurecr.io/langgraph-app
  tag: "latest"

ingress:
  enabled: true
  hosts:
    - host: langgraph.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

### Install Nginx Ingress Controller

```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install Nginx Ingress
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

### Install Cert-Manager (for TLS)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Deploy Application

```bash
# Deploy with Helm
helm upgrade --install langgraph-app ./helm/langgraph-app \
  --namespace production \
  --create-namespace \
  --set image.repository=$ACR_NAME.azurecr.io/langgraph-app \
  --set image.tag=latest \
  --set ingress.hosts[0].host=langgraph.yourdomain.com \
  --wait

# Verify deployment
kubectl get pods -n production
kubectl get services -n production
kubectl get ingress -n production
```

## Step 6: Set Up Monitoring

### Enable Azure Monitor for Containers

```bash
# Enable monitoring
az aks enable-addons \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_CLUSTER \
  --addons monitoring \
  --workspace-resource-id "/subscriptions/<subscription-id>/resourcegroups/$RESOURCE_GROUP/providers/microsoft.operationalinsights/workspaces/<workspace-name>"
```

### Configure Application Insights

1. Create Application Insights resource in Azure Portal
2. Get the connection string
3. Add to Kubernetes secrets or Key Vault
4. Enable in Helm values:

```yaml
env:
  - name: ENABLE_MONITORING
    value: "true"

secrets:
  - name: APPLICATIONINSIGHTS_CONNECTION_STRING
    secretName: langgraph-secrets
    secretKey: appinsights-connection-string
```

## Step 7: Configure Auto-Scaling

The Helm chart includes HPA (Horizontal Pod Autoscaler) by default:

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80
```

Verify HPA:
```bash
kubectl get hpa -n production
```

## Step 8: Set Up CI/CD

### Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. `AZURE_CREDENTIALS`: Service principal credentials
   ```bash
   az ad sp create-for-rbac --name "langgraph-github-actions" \
     --role contributor \
     --scopes /subscriptions/<subscription-id>/resourceGroups/$RESOURCE_GROUP \
     --sdk-auth
   ```

2. `ACR_LOGIN_SERVER`: Your ACR login server
3. `ACR_USERNAME`: ACR username
4. `ACR_PASSWORD`: ACR password

### Update Workflow Files

Edit `.github/workflows/deploy-production.yml` with your resource details:

```yaml
env:
  AZURE_RESOURCE_GROUP: "langgraph-rg"
  AZURE_AKS_CLUSTER: "langgraph-aks"
  NAMESPACE: "production"
```

## Verification

### Check Application Health

```bash
# Get external IP
kubectl get ingress -n production

# Test health endpoint
curl https://langgraph.yourdomain.com/health

# Test API
curl -X POST https://langgraph.yourdomain.com/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### View Logs

```bash
# View application logs
kubectl logs -f deployment/langgraph-app-production -n production

# View all pod logs
kubectl logs -l app.kubernetes.io/name=langgraph-app -n production --tail=100
```

### Monitor Resources

```bash
# Check resource usage
kubectl top pods -n production
kubectl top nodes

# Check HPA status
kubectl get hpa -n production -w
```

## Updating the Application

```bash
# Update image
docker build -t $ACR_NAME.azurecr.io/langgraph-app:v1.0.1 .
docker push $ACR_NAME.azurecr.io/langgraph-app:v1.0.1

# Update deployment
helm upgrade langgraph-app ./helm/langgraph-app \
  --namespace production \
  --set image.tag=v1.0.1 \
  --wait

# Check rollout status
kubectl rollout status deployment/langgraph-app-production -n production
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n production

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Image pull errors

```bash
# Verify ACR integration
az aks check-acr --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --acr $ACR_NAME.azurecr.io
```

### Secret access issues

```bash
# Verify secrets exist
kubectl get secrets -n production

# Check secret content (base64 encoded)
kubectl get secret langgraph-secrets -n production -o yaml
```

## Cleanup

To remove all resources:

```bash
# Delete Helm release
helm uninstall langgraph-app -n production

# Delete AKS cluster
az aks delete --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP --yes --no-wait

# Delete entire resource group (including all resources)
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Next Steps

- Configure custom domain and DNS
- Set up backup and disaster recovery
- Implement network policies
- Configure Azure Front Door for global distribution
- Set up Azure DevOps or GitHub Actions for automated deployments

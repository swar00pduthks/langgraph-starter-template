# Architecture Overview

This document provides a comprehensive overview of the LangGraph Starter Template architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Clients                         │
│                    (Web, Mobile, CLI, APIs)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Front Door / CDN                      │
│                    (Optional Global Distribution)                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Kubernetes Ingress (NGINX)                     │
│                      SSL/TLS Termination                         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Service                        │
│                      (Load Balancer/ClusterIP)                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │FastAPI   │    │FastAPI   │    │FastAPI   │
         │Pod 1     │    │Pod 2     │    │Pod N     │
         └────┬─────┘    └────┬─────┘    └────┬─────┘
              │               │               │
              └───────────────┴───────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │ LangGraph   │ │ CopilotKit  │ │ A2A Protocol│
      │   Agents    │ │   Service   │ │   Service   │
      └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
             │               │               │
             └───────────────┴───────────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   OpenAI     │ │Azure Monitor │ │ Azure Key    │
    │     API      │ │ App Insights │ │    Vault     │
    └──────────────┘ └──────────────┘ └──────────────┘
```

## Component Architecture

### 1. FastAPI Application Layer

```
┌──────────────────────────────────────────────┐
│              FastAPI Application              │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │   Health   │  │   Agent    │            │
│  │  Endpoints │  │  Endpoints │            │
│  └────────────┘  └────────────┘            │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │ CopilotKit │  │    A2A     │            │
│  │  Endpoints │  │  Endpoints │            │
│  └────────────┘  └────────────┘            │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │      Middleware Layer (CORS, etc)      │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### 2. Agent Workflow Architecture

```
┌─────────────────────────────────────────────────┐
│              LangGraph Agent Workflow            │
├─────────────────────────────────────────────────┤
│                                                  │
│  User Query                                      │
│      │                                           │
│      ▼                                           │
│  ┌─────────────┐                                │
│  │   Process   │                                │
│  │   Message   │                                │
│  └──────┬──────┘                                │
│         │                                        │
│         ▼                                        │
│  ┌─────────────┐       ┌──────────────┐        │
│  │  LangChain  │◄─────▶│    OpenAI    │        │
│  │     LLM     │       │     API      │        │
│  └──────┬──────┘       └──────────────┘        │
│         │                                        │
│         ▼                                        │
│  ┌─────────────┐                                │
│  │  Generate   │                                │
│  │  Response   │                                │
│  └──────┬──────┘                                │
│         │                                        │
│         ▼                                        │
│    Agent Response                                │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 3. A2A Protocol Flow

```
┌─────────────┐                    ┌─────────────┐
│   Agent A   │                    │   Agent B   │
└──────┬──────┘                    └──────▲──────┘
       │                                  │
       │ 1. Create Message                │
       │    with Payload                  │
       ▼                                  │
┌──────────────┐                          │
│ Sign Message │                          │
│  (HMAC-256)  │                          │
└──────┬───────┘                          │
       │                                  │
       │ 2. Send Signed Message           │
       ├─────────────────────────────────▶│
       │                                  │
       │                         ┌────────┴────────┐
       │                         │ Verify Signature│
       │                         │   (HMAC-256)    │
       │                         └────────┬────────┘
       │                                  │
       │                         ┌────────┴────────┐
       │                         │ Process Message │
       │                         └────────┬────────┘
       │                                  │
       │ 3. Response                      │
       │◄─────────────────────────────────┤
       │                                  │
       ▼                                  │
```

### 4. CopilotKit Integration Architecture

```
┌──────────────────────────────────────────────────┐
│              CopilotKit Frontend                  │
│                 (AGUI Interface)                  │
└──────────────────────┬───────────────────────────┘
                       │
                       │ REST/SSE
                       ▼
┌──────────────────────────────────────────────────┐
│         FastAPI CopilotKit Endpoints              │
│                                                   │
│  ┌─────────────┐          ┌─────────────┐       │
│  │   /chat     │          │ /chat/stream│       │
│  │   (POST)    │          │    (POST)   │       │
│  └──────┬──────┘          └──────┬──────┘       │
│         │                        │               │
│         └────────────┬───────────┘               │
│                      ▼                           │
│           ┌────────────────────┐                 │
│           │ CopilotKit Service │                 │
│           └──────────┬─────────┘                 │
│                      │                           │
│                      ▼                           │
│           ┌────────────────────┐                 │
│           │   LangChain LLM    │                 │
│           └────────────────────┘                 │
└──────────────────────────────────────────────────┘
```

## Data Flow

### Request Processing Flow

```
1. Client Request
   │
   ├─▶ Ingress Controller (NGINX)
   │   │
   │   ├─▶ TLS Termination
   │   └─▶ Route to Service
   │
   ├─▶ Kubernetes Service
   │   │
   │   └─▶ Load Balance to Pod
   │
   ├─▶ FastAPI Application
   │   │
   │   ├─▶ Middleware (CORS, Auth, etc.)
   │   ├─▶ Route Handler
   │   └─▶ Validate Request (Pydantic)
   │
   ├─▶ Business Logic Layer
   │   │
   │   ├─▶ Agent Processing (LangGraph)
   │   ├─▶ External API Calls (OpenAI)
   │   └─▶ A2A Communication (if needed)
   │
   └─▶ Response
       │
       ├─▶ Format Response (Pydantic)
       ├─▶ Add Headers
       └─▶ Return to Client
```

## Deployment Architecture

### Kubernetes Resources

```
┌─────────────────────────────────────────────────┐
│              Kubernetes Namespace                │
│                  (production)                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │            Deployment                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐│ │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod N   ││ │
│  │  └──────────┘  └──────────┘  └──────────┘│ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │     Horizontal Pod Autoscaler (HPA)        │ │
│  │     Min: 2, Max: 10, Target: 80% CPU      │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │               Service                       │ │
│  │           (ClusterIP/LoadBalancer)          │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │              Ingress                        │ │
│  │      (NGINX with TLS/SSL)                  │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │           Secrets/ConfigMaps                │ │
│  │    (API Keys, Configuration)                │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Security Architecture

### Multi-Layer Security

```
┌─────────────────────────────────────────────────┐
│               Security Layers                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Network Layer                                │
│     ├─ Ingress with TLS/SSL                     │
│     ├─ Network Policies                         │
│     └─ Azure Firewall (optional)                │
│                                                  │
│  2. Application Layer                            │
│     ├─ CORS Configuration                       │
│     ├─ Rate Limiting                            │
│     ├─ Input Validation (Pydantic)              │
│     └─ A2A Message Signing (HMAC)               │
│                                                  │
│  3. Container Layer                              │
│     ├─ Non-root User                            │
│     ├─ Read-only Root Filesystem (where possible)│
│     ├─ Security Context                         │
│     └─ Minimal Base Image                       │
│                                                  │
│  4. Secret Management                            │
│     ├─ Azure Key Vault                          │
│     ├─ Kubernetes Secrets                       │
│     └─ CSI Secret Store Driver                  │
│                                                  │
│  5. Monitoring & Audit                           │
│     ├─ Azure Monitor                            │
│     ├─ Application Insights                     │
│     └─ Audit Logs                               │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Scaling Strategy

### Horizontal Pod Autoscaling

```
Normal Load (2 pods)
┌────────┐  ┌────────┐
│ Pod 1  │  │ Pod 2  │
└────────┘  └────────┘
    │           │
    └─────┬─────┘
          │
    CPU: 30-50%

Medium Load (5 pods)
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Pod 1  │ │ Pod 2  │ │ Pod 3  │ │ Pod 4  │ │ Pod 5  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                         │
                   CPU: 70-80%

High Load (10 pods - max)
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Pod 1  │ │ Pod 2  │ │ Pod 3  │ │ Pod 4  │ │ Pod 5  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Pod 6  │ │ Pod 7  │ │ Pod 8  │ │ Pod 9  │ │ Pod 10 │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                         │
                   CPU: 80-90%
```

## Monitoring & Observability

### Telemetry Architecture

```
┌─────────────────────────────────────────────────┐
│           Application Telemetry                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐│
│  │   Logs     │  │  Metrics   │  │  Traces   ││
│  └──────┬─────┘  └──────┬─────┘  └─────┬─────┘│
│         │               │               │       │
│         └───────────────┴───────────────┘       │
│                         │                       │
│                         ▼                       │
│         ┌──────────────────────────────┐       │
│         │   OpenTelemetry Collector    │       │
│         └──────────────┬───────────────┘       │
│                        │                        │
│         ┌──────────────┴───────────────┐       │
│         │                              │       │
│         ▼                              ▼       │
│  ┌──────────────┐            ┌──────────────┐ │
│  │Azure Monitor │            │ Application  │ │
│  │  Logs        │            │  Insights    │ │
│  └──────────────┘            └──────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Technology Stack

### Core Technologies
- **Python 3.11+**: Application runtime
- **FastAPI**: Web framework
- **LangChain/LangGraph**: Agent framework
- **uv**: Package management
- **Pydantic**: Data validation

### Infrastructure
- **Docker**: Containerization
- **Kubernetes (AKS)**: Orchestration
- **Helm**: Package management
- **NGINX Ingress**: Reverse proxy

### Azure Services
- **AKS**: Kubernetes hosting
- **ACR**: Container registry
- **Key Vault**: Secret management
- **Monitor**: Logging and monitoring
- **Application Insights**: APM

### Development Tools
- **Ruff**: Linting
- **Black**: Code formatting
- **MyPy**: Type checking
- **Pytest**: Testing
- **Pre-commit**: Git hooks

## Best Practices

1. **12-Factor App Principles**: Configuration via environment variables
2. **Immutable Infrastructure**: Containerized deployments
3. **Health Checks**: Liveness and readiness probes
4. **Graceful Shutdown**: Handle SIGTERM signals properly
5. **Resource Limits**: Define CPU and memory limits
6. **Horizontal Scaling**: Use HPA for auto-scaling
7. **Secret Management**: Never commit secrets, use Key Vault
8. **Monitoring**: Comprehensive logging and metrics
9. **Security**: Least privilege, non-root containers
10. **CI/CD**: Automated testing and deployment

## Performance Considerations

- **Async I/O**: FastAPI with async/await for non-blocking operations
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: Implement caching where appropriate
- **Load Balancing**: Kubernetes service for distribution
- **Resource Optimization**: Right-size pod resources

## Next Steps

- [Getting Started](getting-started.md)
- [AKS Deployment](aks-deployment.md)
- [API Documentation](api-documentation.md)
- [Azure Integration](azure-integration.md)

# LangGraph Starter Template

A production-ready starter template for building LangGraph-based AI agent applications with FastAPI, CopilotKit, A2A protocol support, and Azure Kubernetes Service (AKS) deployment capabilities.

[![CI](https://github.com/swar00pduthks/langgraph-starter-template/workflows/CI%20-%20Lint%20and%20Test/badge.svg)](https://github.com/swar00pduthks/langgraph-starter-template/actions)
[![Docker](https://github.com/swar00pduthks/langgraph-starter-template/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/swar00pduthks/langgraph-starter-template/actions)

## 🚀 Features

### Core Technologies
- **LangChain & LangGraph**: Latest versions for building sophisticated AI agent workflows
- **FastAPI**: High-performance async API framework
- **CopilotKit Integration**: AGUI (Agent Graphical User Interface) for chatbot-like interactions
- **A2A Protocol**: Secure Agent-to-Agent communication with HMAC signing
- **MCP Compatible**: Microsoft Commercial Platform integration ready

### Production Features
- **uv**: Fast Python package installer and dependency management
- **Docker**: Multi-stage optimized Dockerfile for secure containerization
- **Kubernetes/Helm**: Complete Helm charts with HPA, Ingress, RBAC
- **CI/CD**: GitHub Actions workflows for linting, testing, and AKS deployment
- **Azure Integration**: Key Vault, App Insights, and Azure Monitor support
- **Security**: Non-root containers, secret management, signed A2A messages

## 📋 Prerequisites

- Python 3.11+
- uv (https://github.com/astral-sh/uv)
- Docker & Docker Compose
- Azure CLI (for AKS deployment)
- kubectl & Helm (for Kubernetes deployment)
- OpenAI API Key

## 🏁 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/swar00pduthks/langgraph-starter-template.git
   cd langgraph-starter-template
   ```

2. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Create virtual environment and install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r pyproject.toml
   uv pip install -e ".[dev]"
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the application**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8000
```

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [AKS Deployment Guide](docs/aks-deployment.md)
- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api-documentation.md)
- [Azure Integration](docs/azure-integration.md)

## 🏗️ Project Structure

```
.
├── app/
│   ├── api/              # API endpoints
│   │   ├── agent.py      # Agent chat endpoints
│   │   ├── copilot.py    # CopilotKit integration
│   │   ├── a2a.py        # A2A protocol endpoints
│   │   └── health.py     # Health check endpoints
│   ├── agents/           # LangGraph agents
│   │   └── demo_agent.py # Demo agent implementation
│   ├── core/             # Core configuration
│   │   └── config.py     # Settings and environment
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   │   ├── a2a_protocol.py    # A2A implementation
│   │   └── copilot_service.py # CopilotKit service
│   └── main.py           # FastAPI application
├── helm/                 # Helm charts for Kubernetes
├── tests/                # Test suite
├── .github/              # GitHub Actions workflows
├── Dockerfile            # Production container
├── docker-compose.yml    # Local development
├── pyproject.toml        # Project dependencies (uv compatible)
└── uv.lock              # Dependency lock file

```

## 🔌 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /ready` - Readiness probe
- `GET /live` - Liveness probe

### Agent
- `POST /api/v1/agent/chat` - Chat with the agent
- `GET /api/v1/agent/status` - Get agent status

### CopilotKit
- `POST /api/v1/copilot/chat` - CopilotKit compatible chat
- `POST /api/v1/copilot/chat/stream` - Streaming chat

### A2A Protocol
- `POST /api/v1/a2a/send` - Send A2A message
- `POST /api/v1/a2a/receive` - Receive A2A message
- `GET /api/v1/a2a/status` - A2A protocol status

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_health.py -v
```

## 🔧 Development

### Linting & Formatting

```bash
# Run ruff linter
uv run ruff check app/

# Run black formatter
uv run black app/

# Run type checking
uv run mypy app/

# Run all checks
uv run ruff check app/ && uv run black app/ && uv run mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### Dependency Management with uv

```bash
# Add a new dependency
uv pip install <package-name>

# Update dependencies
uv pip install --upgrade -r pyproject.toml

# Lock dependencies
uv lock

# Sync environment with lock file
uv sync
```

## 🚢 Deployment

### Deploy to AKS

See [AKS Deployment Guide](docs/aks-deployment.md) for detailed instructions.

Quick deploy:

```bash
# Login to Azure
az login

# Set context to your AKS cluster
az aks get-credentials --resource-group <rg-name> --name <cluster-name>

# Deploy with Helm
helm upgrade --install langgraph-app ./helm/langgraph-app \
  --namespace production \
  --create-namespace \
  --set image.tag=latest
```

## 🔐 Security

- **Secret Management**: Use Azure Key Vault or Kubernetes secrets
- **A2A Protocol**: HMAC-SHA256 message signing
- **Container Security**: Non-root user, minimal base image
- **Network Security**: Ingress with TLS, network policies

## 🔑 Environment Variables

Key environment variables (see `.env.example`):

```bash
# Required
OPENAI_API_KEY=your-key-here

# Optional
DEBUG=false
A2A_SECRET_KEY=your-secret-key
AZURE_KEY_VAULT_NAME=your-keyvault
ENABLE_MONITORING=true
APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string
```

## 📊 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Ingress   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  FastAPI    │────▶│  LangGraph   │
│  Service    │     │   Agents     │
└──────┬──────┘     └──────────────┘
       │
       ├────────▶ A2A Protocol
       │
       ├────────▶ CopilotKit/AGUI
       │
       └────────▶ Azure Services
                 (Key Vault, Monitor)
```

See [Architecture Overview](docs/architecture.md) for detailed diagrams.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [FastAPI](https://fastapi.tiangolo.com/)
- [CopilotKit](https://copilotkit.ai/)
- [uv](https://github.com/astral-sh/uv)

## 📧 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/swar00pduthks/langgraph-starter-template/issues)
- Documentation: [docs/](docs/)

---

**Built with ❤️ for the AI agent community**

# Getting Started with LangGraph Starter Template

This guide will help you get started with the LangGraph Starter Template quickly.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **uv**: Fast Python package installer
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Docker** (optional, for containerized development): [Install Docker](https://docs.docker.com/get-docker/)
- **OpenAI API Key**: [Get API Key](https://platform.openai.com/api-keys)

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/swar00pduthks/langgraph-starter-template.git
cd langgraph-starter-template
```

### Step 2: Set Up Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional
DEBUG=true
A2A_SECRET_KEY=your-secret-key-for-development
```

### Step 3: Install Dependencies with uv

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r pyproject.toml
uv pip install -e ".[dev]"
```

### Step 4: Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Using Docker

If you prefer to use Docker:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Stop the services
docker-compose down
```

## Testing the Application

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "app_name": "LangGraph Starter Template"
}
```

### Chat with Agent

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Tell me about LangGraph."
  }'
```

### CopilotKit Chat

```bash
curl -X POST http://localhost:8000/api/v1/copilot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is AI?"}
    ]
  }'
```

### A2A Protocol Message

```bash
curl -X POST http://localhost:8000/api/v1/a2a/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "agent-1",
    "receiver_id": "agent-2",
    "message_type": "query",
    "payload": {"question": "What is the weather?"}
  }'
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## Development Workflow

### Code Formatting and Linting

```bash
# Format code with Black
uv run black app/ tests/

# Lint with Ruff
uv run ruff check app/ tests/

# Fix auto-fixable issues
uv run ruff check --fix app/ tests/

# Type checking with mypy
uv run mypy app/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

## Project Structure Overview

```
langgraph-starter-template/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── agents/            # LangGraph agents
│   ├── core/              # Core configuration
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   └── main.py            # FastAPI app entry point
├── tests/                 # Test suite
├── helm/                  # Kubernetes Helm charts
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD pipelines
├── pyproject.toml         # Dependencies (uv compatible)
├── uv.lock               # Dependency lock file
└── README.md              # Main documentation
```

## Next Steps

- [Explore the API Documentation](api-documentation.md)
- [Learn about the Architecture](architecture.md)
- [Deploy to Azure AKS](aks-deployment.md)
- [Configure Azure Integration](azure-integration.md)

## Common Issues

### Issue: Module not found errors

**Solution**: Make sure you've installed the dependencies and activated the virtual environment:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r pyproject.toml
```

### Issue: OpenAI API errors

**Solution**: Verify your API key is set in `.env` and is valid:
```bash
echo $OPENAI_API_KEY  # Check if set
```

### Issue: Port already in use

**Solution**: Change the port or kill the process using port 8000:
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill process on port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

## Support

If you encounter issues:
1. Check the [GitHub Issues](https://github.com/swar00pduthks/langgraph-starter-template/issues)
2. Review the [documentation](../README.md)
3. Create a new issue with details about your problem

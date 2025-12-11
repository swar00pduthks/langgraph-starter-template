# API Documentation

Complete API reference for the LangGraph Starter Template.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication. For production, consider adding:
- API Keys
- OAuth2/JWT tokens
- Azure AD integration

## Health & Status Endpoints

### GET /health

Health check endpoint for monitoring.

**Response**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "app_name": "LangGraph Starter Template"
}
```

**Status Codes**
- `200 OK`: Application is healthy

---

### GET /ready

Readiness probe for Kubernetes.

**Response**
```json
{
  "status": "ready"
}
```

**Status Codes**
- `200 OK`: Application is ready to serve traffic

---

### GET /live

Liveness probe for Kubernetes.

**Response**
```json
{
  "status": "alive"
}
```

**Status Codes**
- `200 OK`: Application is alive

---

## Agent Endpoints

### POST /api/v1/agent/chat

Chat with the LangGraph agent.

**Request Body**
```json
{
  "message": "string (required)",
  "session_id": "string (optional)",
  "metadata": {
    "key": "value"
  }
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is LangGraph?",
    "session_id": "user-123"
  }'
```

**Response**
```json
{
  "response": "LangGraph is a framework for building stateful, multi-actor applications with LLMs...",
  "session_id": "user-123",
  "metadata": {
    "steps": 2,
    "message_count": 2
  }
}
```

**Status Codes**
- `200 OK`: Successful response
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Processing error

---

### GET /api/v1/agent/status

Get agent status and capabilities.

**Response**
```json
{
  "status": "running",
  "agent_type": "DemoAgent",
  "capabilities": ["chat", "query_processing"]
}
```

**Status Codes**
- `200 OK`: Successful response

---

## CopilotKit Endpoints

### POST /api/v1/copilot/chat

CopilotKit-compatible chat endpoint.

**Request Body**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "model": "gpt-4",
  "stream": false
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/copilot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is AI?"}
    ]
  }'
```

**Response**
```json
{
  "message": {
    "role": "assistant",
    "content": "AI, or Artificial Intelligence, refers to...",
    "name": null
  },
  "finish_reason": "stop"
}
```

**Status Codes**
- `200 OK`: Successful response
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Processing error

---

### POST /api/v1/copilot/chat/stream

Streaming chat endpoint for real-time responses.

**Request Body**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Tell me a story"
    }
  ],
  "stream": true
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/copilot/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me about machine learning"}
    ],
    "stream": true
  }'
```

**Response** (Server-Sent Events)
```
event: message
data: Machine

event: message
data:  learning

event: message
data:  is...

event: done
data: [DONE]
```

**Status Codes**
- `200 OK`: Streaming response
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Processing error

---

## A2A Protocol Endpoints

### POST /api/v1/a2a/send

Send a message using the Agent-to-Agent protocol.

**Request Body**
```json
{
  "sender_id": "agent-1",
  "receiver_id": "agent-2",
  "message_type": "query",
  "payload": {
    "question": "What is the weather?",
    "location": "New York"
  },
  "timestamp": "1234567890",
  "signature": "optional-will-be-generated"
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/a2a/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "agent-1",
    "receiver_id": "agent-2",
    "message_type": "query",
    "payload": {
      "question": "What is the weather?"
    }
  }'
```

**Response**
```json
{
  "success": true,
  "message": "Message sent from agent-1 to agent-2",
  "data": {
    "message_id": "agent-1-1234567890"
  }
}
```

**Status Codes**
- `200 OK`: Message sent successfully
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Processing error

---

### POST /api/v1/a2a/receive

Receive and process an A2A message.

**Request Body**
```json
{
  "sender_id": "agent-1",
  "receiver_id": "agent-2",
  "message_type": "query",
  "payload": {
    "question": "What is the weather?"
  },
  "timestamp": "1234567890",
  "signature": "hmac-sha256-signature"
}
```

**Example Request**
```bash
curl -X POST http://localhost:8000/api/v1/a2a/receive \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "agent-1",
    "receiver_id": "agent-2",
    "message_type": "query",
    "payload": {
      "question": "What is the weather?"
    },
    "timestamp": "1234567890",
    "signature": "valid-signature-here"
  }'
```

**Response**
```json
{
  "success": true,
  "message": "Message processed successfully",
  "data": {
    "answer": "This is a demo response to your query"
  }
}
```

**Response** (Invalid Signature)
```json
{
  "success": false,
  "message": "Invalid message signature",
  "data": null
}
```

**Status Codes**
- `200 OK`: Message processed
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Processing error

---

### GET /api/v1/a2a/status

Get A2A protocol status.

**Response**
```json
{
  "enabled": true,
  "protocol_version": "1.0",
  "supported_message_types": ["query", "response", "action"]
}
```

**Status Codes**
- `200 OK`: Successful response

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Status Codes

- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Service temporarily unavailable

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Consider implementing rate limiting per IP/API key
- Use Redis for distributed rate limiting
- Configure appropriate limits based on your use case

---

## Interactive Documentation

The API also provides interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly from the browser
- Generate code snippets

---

## WebSocket Support (Future)

WebSocket endpoints for real-time bidirectional communication will be added in future versions.

---

## SDK Examples

### Python Example

```python
import httpx

# Chat with agent
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/agent/chat",
        json={"message": "Hello, agent!"}
    )
    data = response.json()
    print(data["response"])
```

### JavaScript Example

```javascript
// Chat with agent
const response = await fetch('http://localhost:8000/api/v1/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Hello, agent!'
  })
});

const data = await response.json();
console.log(data.response);
```

### cURL Examples

See individual endpoint sections above for cURL examples.

---

## Next Steps

- [Getting Started Guide](getting-started.md)
- [Architecture Overview](architecture.md)
- [AKS Deployment](aks-deployment.md)

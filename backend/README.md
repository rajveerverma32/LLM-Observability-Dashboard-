# LLM Observability Dashboard - Backend

A production-ready FastAPI backend for comprehensive LLM observability and monitoring.

## 🚀 Features

### Authentication & RBAC
- JWT-based authentication
- Role-based access control (Admin/Viewer)
- User registration and login
- Secure password hashing with bcrypt

### Core Observability
- **LLM Call Tracking**: Measures latency, token usage, success/error
- **Cost Estimation**: Calculates costs per call based on token usage
- **Performance Metrics**: Tracks latency distribution and error rates
- **Quality Feedback**: Captures user ratings and feedback

### Admin Features
- System settings management
- **Claude Haiku 4.5 Toggle**: Enable/disable for all clients
- Token limits configuration
- Response caching controls
- Cost tracking

### Metrics & Analytics
- Daily token usage aggregation
- Latency distribution analysis
- Error rate tracking
- Cost analysis
- Time-series data for dashboard visualization

## 🛠️ Tech Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL/SQLite**: Data persistence
- **JWT (python-jose)**: Token-based authentication
- **Pydantic**: Request/response validation
- **Passlib + bcrypt**: Secure password handling

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL (optional, SQLite used by default for development)
- pip

## 🚀 Quick Start

### 1. Installation

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database & Run Server

```bash
python main.py
```

The server will:
- Create database tables
- Seed default admin/viewer users and LLM models
- Start on `http://localhost:8000`

### 4. Access API Documentation

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 👤 Demo Credentials

After initialization, you can log in with:

**Admin User:**
- Email: `admin@example.com`
- Password: `admin123`
- Access: Full system including settings

**Viewer User:**
- Email: `viewer@example.com`
- Password: `viewer123`
- Access: Dashboard metrics and feedback only

## 📁 Project Structure

```
backend/
├── auth/
│   ├── jwt.py              # JWT token generation/validation
│   ├── dependencies.py     # FastAPI dependency injection
│   └── __init__.py
├── models/
│   └── __init__.py         # SQLAlchemy ORM models
├── schemas/
│   └── __init__.py         # Pydantic request/response schemas
├── routes/
│   ├── auth.py             # Authentication endpoints
│   ├── llm.py              # LLM call logging
│   ├── metrics.py          # Metrics & analytics
│   ├── feedback.py         # Feedback management
│   ├── settings.py         # Admin settings
│   └── __init__.py
├── services/
│   ├── user_service.py     # User operations
│   ├── metrics_service.py  # Metrics aggregation
│   └── __init__.py
├── observability/
│   ├── wrapper.py          # LLM call observability wrapper
│   ├── mock_llm.py         # Mock LLM for testing
│   └── __init__.py
├── db/
│   └── __init__.py         # Database configuration
├── utils/
│   └── __init__.py         # Utility functions
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration template
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### LLM Logging
- `POST /llm/log-call` - Log LLM API call with metrics

### Metrics
- `GET /metrics/summary` - Get aggregated metrics (30-day window)
- `GET /metrics/token-usage` - Get daily token usage
- `GET /metrics/latency` - Get latency distribution
- `GET /metrics/error-rate` - Get error rate over time
- `GET /metrics/cost` - Get total cost

### Feedback
- `POST /feedback` - Submit feedback for LLM call
- `GET /feedback` - Get all feedback (Admin only)

### Settings (Admin Only)
- `GET /settings` - Get system settings
- `PUT /settings` - Update system settings (Claude Haiku 4.5 toggle, etc.)

## 📊 Database Models

### User
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password
- `role`: ADMIN or VIEWER
- `created_at`, `updated_at`: Timestamps

### LLMModel
- `id`: Primary key
- `name`: Model name (e.g., "gpt-4")
- `provider`: Provider (OpenAI, Anthropic, etc.)
- `cost_per_1k_tokens`: Pricing information

### LLMCallLog
- `id`: Primary key
- `user_id`: Foreign key to User
- `model_id`: Foreign key to LLMModel
- `prompt_tokens`: Input token count
- `completion_tokens`: Output token count
- `latency_ms`: Response time in milliseconds
- `status`: success/error/timeout
- `error_message`: Error details if applicable
- `created_at`: Timestamp

### CostLog
- `id`: Primary key
- `llm_call_id`: Foreign key to LLMCallLog
- `estimated_cost`: Calculated cost for the call

### Feedback
- `id`: Primary key
- `llm_call_id`: Foreign key to LLMCallLog
- `user_id`: Foreign key to User
- `rating`: 1-5 rating
- `comment`: User feedback text

### SystemSettings
- `id`: Primary key
- `claude_haiku_45_enabled`: Feature flag for Claude Haiku 4.5
- `max_tokens_per_request`: Token limit
- `enable_caching`: Caching toggle
- `updated_at`: Last modification timestamp

## 🧪 Usage Examples

### Register & Login

```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Log LLM Call

```bash
curl -X POST "http://localhost:8000/llm/log-call" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "prompt_tokens": 50,
    "completion_tokens": 150,
    "total_tokens": 200,
    "latency_ms": 245.5,
    "status": "success"
  }'
```

### Get Metrics Summary

```bash
curl -X GET "http://localhost:8000/metrics/summary?days=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update System Settings (Admin Only)

```bash
curl -X PUT "http://localhost:8000/settings" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claude_haiku_45_enabled": true,
    "max_tokens_per_request": 8192,
    "enable_caching": true
  }'
```

## 🔒 Security Considerations

1. **JWT Secret**: Change `SECRET_KEY` in `.env` for production
2. **CORS**: Configure `CORS_ORIGINS` appropriately
3. **Database**: Use PostgreSQL in production, not SQLite
4. **HTTPS**: Use HTTPS in production
5. **Rate Limiting**: Consider adding rate limiting middleware
6. **Input Validation**: All inputs are validated with Pydantic

## 📝 Observability Wrapper Example

The `LLMObservabilityWrapper` class wraps LLM calls to measure metrics:

```python
from observability.wrapper import LLMObservabilityWrapper
from observability.mock_llm import mock_gpt4_api_call

# Create wrapper
wrapper = LLMObservabilityWrapper(db, user_id=1, model_id=1)

# Call LLM with automatic observability
result = wrapper.call_llm(mock_gpt4_api_call, "What is AI?")

print(result)
# {
#   "success": True,
#   "response": "AI is...",
#   "metrics": {
#     "latency_ms": 245.5,
#     "prompt_tokens": 5,
#     "completion_tokens": 150,
#     "total_tokens": 155,
#     "estimated_cost": 0.00465
#   },
#   "log_id": 1
# }
```

## 🧪 Testing

Run tests:

```bash
pytest
```

## 🚀 Production Deployment

### Using PostgreSQL

Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/llm_observability
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Run:
```bash
docker build -t llm-observability-backend .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... llm-observability-backend
```

## 🤝 Integration with Frontend

The React frontend communicates with this backend via:

1. **Authentication**: Login to get JWT token
2. **Request Headers**: Include `Authorization: Bearer {token}`
3. **API Base URL**: Configure in frontend `.env`

Example frontend setup:

```typescript
const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});
```

## 📚 API Response Format

All responses follow a consistent format:

```json
{
  "data": {},
  "status": "success",
  "message": "Operation successful"
}
```

Errors:

```json
{
  "detail": "Error message",
  "status": 400
}
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
kill -9 $(lsof -t -i:8000)
```

### Database Lock (SQLite)
```bash
rm test.db
python main.py  # Will recreate with fresh data
```

### Import Errors
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python main.py
```

## 📄 License

MIT

## 👨‍💻 Author

Built for enterprise LLM observability

## 📞 Support

For issues and questions, refer to the API documentation at `/docs`

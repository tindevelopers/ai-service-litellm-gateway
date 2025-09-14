# AI-as-a-Service LiteLLM Gateway

A comprehensive AI-as-a-Service platform that provides intelligent abstraction layers on top of multiple LLM providers, offering specialized services for content generation, customer support, and business automation.

## 🚀 Features

### ✅ Implemented
- **Multi-Provider LLM Access**: Unified API for 100+ LLM providers via LiteLLM
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API
- **Task-Specific Services**: Specialized endpoints for customer support
- **Model Management**: Dynamic model listing based on available API keys
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Health Monitoring**: Health and readiness endpoints for deployment
- **Structured Logging**: Detailed logging with request/response tracking
- **Prometheus Metrics**: Built-in metrics collection for monitoring
- **CI/CD Pipeline**: Automated deployment to Google Cloud Run via GitHub Actions
- **Google Cloud Integration**: Full GCP setup with proper IAM permissions and API enablement

### 🚧 In Development
- **Semantic Caching**: 30-70% cost savings through Redis-based caching
- **API Key Authentication**: Secure access control with API keys
- **Rate Limiting**: Built-in protection and cost control
- **Usage Analytics**: Comprehensive tracking and billing integration
- **Database Integration**: User management and usage tracking

## 🏗️ Architecture

### Three-Tier Architecture
1. **Client Applications Layer**: Blog Writers, Chatbots, Customer Support tools
2. **Specialized APIs Layer**: Task-specific services (Blog Writer, Customer Support, etc.)
3. **Core Gateway Layer**: LiteLLM proxy with intelligent routing

### Technology Stack
- **API Framework**: FastAPI with async support
- **LLM Gateway**: LiteLLM for multi-provider access
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for semantic caching and rate limiting
- **Deployment**: Docker containers on Render
- **Monitoring**: Prometheus metrics and structured logging

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional)
- PostgreSQL 15+ (optional for basic testing)
- Redis 7+ (optional for caching)

### Quick Start (Automated Setup)

1. **Clone the repository**
   ```bash
   git clone https://github.com/tindevelopers/ai-service-litellm-gateway.git
   cd ai-service-litellm-gateway
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure your API keys**
   ```bash
   # Edit the .env file with your actual API keys
   nano .env
   
   # At minimum, add one LLM provider API key:
   OPENAI_API_KEY=your-openai-api-key-here
   # or
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

4. **Start the server**
   ```bash
   source venv/bin/activate
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # List available models
   curl http://localhost:8000/v1/models
   
   # Chat completion
        curl -X POST "http://localhost:8080/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

### Manual Setup

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Metrics: http://localhost:8000/metrics

## 📚 API Documentation

### Core Endpoints

#### Health & Status
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /metrics` - Prometheus metrics

#### Models
- `GET /v1/models` - List available models

#### Chat Completions (OpenAI-Compatible)
- `POST /v1/chat/completions` - Create chat completion

```bash
        curl -X POST "http://localhost:8080/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 150
  }'
```

#### Specialized Services

##### Customer Support
- `POST /v1/support/respond` - Generate support responses

### Interactive API Documentation

Visit `http://localhost:8080/docs` for interactive Swagger documentation with all endpoints, request/response schemas, and the ability to test API calls directly from your browser.

### Local Development Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Configure your .env file with:
   # - Database URL (PostgreSQL)
   # - Redis URL
   # - LLM Provider API Keys (OpenAI, Anthropic, etc.)
   # - Other configuration options
   ```

3. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker for dependencies only
   docker-compose up -d db redis
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Environment Configuration

Key environment variables to configure in your `.env` file:

```bash
# Required: Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_gateway

# Required: Redis
REDIS_URL=redis://localhost:6379

# Required: Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Required: At least one LLM provider API key
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Optional: Additional providers
GOOGLE_API_KEY=your-google-api-key
COHERE_API_KEY=your-cohere-api-key
```

### Testing the Installation

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **List Available Models**
   ```bash
   curl http://localhost:8000/v1/models
   ```

3. **Test Chat Completion**
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello!"}]
     }'
   ```

 

## 📊 API Endpoints

### Core Gateway
- `POST /v1/chat/completions` - OpenAI-compatible chat completions
- `POST /v1/completions` - Text completions
- `GET /v1/models` - List available models

### Specialized Services
- `POST /v1/support/classify` - Customer support ticket classification
- `POST /v1/support/respond` - Automated support responses

### Management
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /auth/token` - Authentication

## 🚀 Deployment

The platform is designed for deployment on Render with automatic CI/CD via GitHub Actions.

## 📈 Monitoring and Analytics

- **Health Checks**: `/health` endpoint for uptime monitoring
- **Metrics**: Prometheus metrics at `/metrics`
- **Logging**: Structured JSON logs with request tracing
- **Usage Tracking**: Per-API key usage and cost tracking

## 🔐 Authentication

The platform uses API key-based authentication with rate limiting and usage tracking.

## 📁 Project Structure

```
src/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/                   # Core application modules
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection and setup
│   ├── redis.py           # Redis connection and caching
│   └── logging.py         # Structured logging setup
├── models/                 # SQLAlchemy database models
│   ├── user.py            # User model
│   ├── api_key.py         # API key model
│   └── usage.py           # Usage tracking model
├── api/                    # API routes and endpoints
│   └── v1/
│       ├── router.py      # Main API router
│       └── endpoints/     # Individual endpoint modules
│           ├── auth.py    # Authentication endpoints
│           ├── chat.py    # Chat completion endpoints
│           ├── models.py  # Model listing endpoints
│           └── support.py # Customer support service
├── services/               # Business logic services
└── utils/                  # Utility functions

tests/
├── unit/                   # Unit tests
└── integration/            # Integration tests

alembic/                    # Database migrations
├── versions/               # Migration files
└── env.py                 # Alembic configuration

deploy/                     # Deployment scripts
├── setup-gcp.sh           # Google Cloud setup
└── setup-mcp-credentials.sh # MCP credentials setup
```

## 🔧 Development Features

### Current Implementation Status

✅ **Completed Features:**
- FastAPI application with async support
- Database models (User, APIKey, Usage)
- Redis caching infrastructure
- OpenAI-compatible chat completions endpoint
- Customer support ticket classification and response
- Health checks and monitoring endpoints
- Docker containerization
- Database migrations with Alembic
- Comprehensive test suite
- CI/CD pipeline configuration

🚧 **Planned Features:**
- LiteLLM integration for multi-provider support
- API key authentication and rate limiting
- Semantic caching implementation
- Real-time usage tracking and billing
- Advanced monitoring with Prometheus metrics
- Cost optimization algorithms
- Enhanced security features

### Next Steps for Production

1. **Configure LLM Provider API Keys**: Add your API keys to the `.env` file
2. **Set up Authentication**: Implement API key generation and validation
3. **Enable Caching**: Configure Redis-based semantic caching
4. **Deploy to Cloud**: Use the provided deployment configurations
5. **Monitor Usage**: Set up usage tracking and billing integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
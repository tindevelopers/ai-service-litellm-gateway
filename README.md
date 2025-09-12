# AI-as-a-Service LiteLLM Gateway

A comprehensive AI-as-a-Service platform that provides intelligent abstraction layers on top of multiple LLM providers, offering specialized services for content generation, customer support, and business automation.

## 🚀 Features

- **Multi-Provider LLM Access**: Unified API for 100+ LLM providers via LiteLLM
- **Task-Specific Routing**: Pre-configured model selection for specific use cases
- **Cost Optimization**: Intelligent routing for best price/performance ratio
- **Semantic Caching**: 30-70% cost savings through Redis-based caching
- **Rate Limiting**: Built-in protection and cost control
- **Usage Analytics**: Comprehensive tracking and billing integration

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
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/tindevelopers/ai-service-litellm-gateway.git
   cd ai-service-litellm-gateway
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

## 📊 API Endpoints

### Core Gateway
- `POST /v1/chat/completions` - OpenAI-compatible chat completions
- `POST /v1/completions` - Text completions
- `GET /v1/models` - List available models

### Specialized Services
- `POST /v1/blog/generate` - Blog content generation
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
# AI Agent Operating System Backend

A comprehensive backend system for managing AI agents across different software development modules including Code Quality, DevOps, Documentation, Testing, Security, and Project Management.

## 🚀 Features

- **Multi-Module AI Agents**: Specialized agents for different development areas
- **Vector Database**: PostgreSQL with pgvector for semantic search
- **File Ingestion**: Support for PDFs, images, archives, and text files
- **Background Processing**: Redis + RQ for async file processing
- **REST API**: FastAPI-based API for frontend integration
- **External Integrations**: GitHub, JIRA, Slack, GitLab, SonarQube, Snyk, Confluence support

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 13+ with pgvector extension
- Redis 6+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd Backend
   ```

2. **Set environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your actual API keys and configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Check status**
   ```bash
   docker-compose ps
   ```

### Option 2: Manual Setup

1. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL**
   ```bash
   # Install PostgreSQL and pgvector extension
   # Create database 'ai' with user 'ai'
   # Run init.sql script
   ```

3. **Set up Redis**
   ```bash
   # Install and start Redis server
   redis-server
   ```

4. **Set environment variables**
   ```bash
   export OPENAI_API_KEY="your_key_here"
   export MISTRAL_API_KEY="your_key_here"
   # ... other variables
   ```

5. **Run setup script**
   ```bash
   python setup.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Used By |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | **Yes** | Core functionality |
| `MISTRAL_API_KEY` | Mistral API key for OCR | **Yes** | PDF processing |
| `PG_HOST` | PostgreSQL host | No (default: localhost) | Database connection |
| `PG_PORT` | PostgreSQL port | No (default: 5532) | Database connection |
| `PG_DATABASE` | PostgreSQL database | No (default: ai) | Database connection |
| `PG_USER` | PostgreSQL user | No (default: ai) | Database connection |
| `PG_PASSWORD` | PostgreSQL password | No (default: ai) | Database connection |
| `REDIS_URL` | Redis connection URL | No (default: redis://localhost:6379/0) | Background jobs |
| `GITHUB_TOKEN` | GitHub token for PR comments, commit status, workflows | No | GitHub integration |
| `GITLAB_TOKEN` | GitLab token for MR comments | No | GitLab integration |
| `GITLAB_TRIGGER_TOKEN` | GitLab token for pipeline triggers | No | GitLab CI/CD |
| `JIRA_URL` | JIRA instance URL | No | Issue creation |
| `JIRA_EMAIL` | JIRA username/email | No | Issue creation |
| `JIRA_API_TOKEN` | JIRA API token | No | Issue creation |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | No | Team notifications |
| `SONARQUBE_TOKEN` | SonarQube token for quality gates | No | Code quality |
| `CONFLUENCE_USER` | Confluence username | No | Documentation |
| `CONFLUENCE_TOKEN` | Confluence token | No | Documentation |

## 🚀 Usage

### Start the Backend

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Start the Worker

```bash
python worker.py
```

### API Endpoints

- `GET /health` - Health check
- `GET /modules` - List available modules
- `GET /modules/{module_key}/chats` - List chats for a module
- `POST /modules/{module_key}/chats` - Create a new chat
- `GET /chats/{chat_id}/messages` - Get chat messages
- `POST /chats/{chat_id}/messages` - Send a message
- `POST /upload` - Upload files for ingestion
- `GET /jobs/{job_id}` - Check job status

### File Upload

Supported file types:
- **Archives**: `.zip`, `.jar`, `.war`, `.ear`, `.tar.gz`, `.tgz`, `.tar`
- **Documents**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`
- **Text**: `.md`, `.yaml`, `.yml`, `.json`, `.xml`, `.csv`, `.log`, `.txt`, `.diff`, `.patch`, `.info`, `.env`, `.sh`, `.tf`, `Dockerfile`

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│                 │◄──►│   Backend       │◄──►│   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis + RQ    │
                       │   Worker        │
                       └─────────────────┘
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error: No module named 'agno'**
   ```bash
   pip install agno
   ```

2. **Import Error: No module named 'pgvector'**
   ```bash
   pip install pgvector
   ```

3. **Import Error: No module named 'requests'**
   ```bash
   pip install requests
   ```

4. **PostgreSQL Connection Failed**
   - Check if PostgreSQL is running
   - Verify connection parameters in environment variables
   - Ensure pgvector extension is installed

5. **Redis Connection Failed**
   - Check if Redis server is running
   - Verify REDIS_URL environment variable

6. **API Key Errors**
   - Set OPENAI_API_KEY and MISTRAL_API_KEY environment variables
   - Verify API keys are valid

7. **Docker Build Fails**
   - Check if all packages in requirements.txt are available
   - Ensure Docker has enough memory/disk space

### Logs

Check logs for detailed error information:
```bash
docker-compose logs backend
docker-compose logs worker
docker-compose logs postgres
docker-compose logs redis
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check Docker services health
docker-compose ps
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Run `python setup.py` to diagnose issues
4. Create an issue in the repository

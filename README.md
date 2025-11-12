# Sales CRM

A minimal proof-of-concept CRM system for managing sales leads.

## Features

- Lead management (CRUD operations)
- Multi-tenant support
- REST API with OpenAPI docs
- React frontend
- AI-powered email generation (OpenAI)

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite
- **Deployment**: Docker Compose

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- 2GB RAM minimum
- Ports 5173, 8000, 5432 available
- (Optional) OpenAI API key for AI email generation

## Quick Start

1. Clone and navigate to the directory:
   ```bash
   git clone <repository-url>
   cd sales-crm
   ```

2. Copy environment template:
   ```bash
   cp .env.example .env
   ```

3. (Optional) Edit `.env` to add your OpenAI API key

4. Start the services:
   
   **Windows:**
   ```powershell
   .\start.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Or use Docker Compose directly:**
   ```bash
   docker-compose up --build
   ```

5. Access the application:
   - **Frontend**: http://localhost:5173
   - **API Docs**: http://localhost:8000/docs
   - **API Health**: http://localhost:8000/health

## Development

### Health Check

```bash
# Windows
.\health.ps1

# Linux/Mac
curl http://localhost:8000/health
```

### View Logs

```bash
docker-compose logs -f
```

### Run Tests

```bash
py tests\check_database.py
py tests\test_email_generation.py
```

## Project Structure

```
sales-crm/
├── backend/          # FastAPI application
├── frontend/         # React application
├── database/         # SQL initialization
├── tests/            # Test scripts
└── docker-compose.yml
```

## API Endpoints

- `GET /api/tenants` - List tenants
- `GET /api/leads` - List leads (filterable by tenant)
- `POST /api/leads` - Create lead
- `PUT /api/leads/{id}` - Update lead
- `DELETE /api/leads/{id}` - Delete lead
- `POST /api/ai/generate-email` - Generate AI email

See full API documentation at `/docs` when running.

## Troubleshooting

### Port Conflicts

If ports are already in use, edit `docker-compose.yml` port mappings:
```yaml
ports:
  - "8080:8000"  # Change left port number
```

### Database Issues

Reset the database:
```bash
docker-compose down -v
docker-compose up --build
```

### Docker Not Running

Make sure Docker Desktop is running before starting the application.

## Environment Variables

See `.env.example` for all configuration options. Key variables:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - Database credentials
- `OPENAI_API_KEY` - Required for AI email generation (optional)

## License

Apache-2.0


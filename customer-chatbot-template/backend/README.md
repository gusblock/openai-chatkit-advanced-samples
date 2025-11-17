# Customer Chatbot Backend

FastAPI backend service with ChatKit and OpenAI Agents SDK integration.

## Quick Start

1. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv pip install -e .

   # Or using pip
   pip install -e .
   ```

2. **Configure environment**:
   ```bash
   # Copy template and fill in values
   cp ../.env.template .env

   # Required variables:
   # - OPENAI_API_KEY
   # - VECTOR_STORE_ID (create with scripts/setup-vector-store.py)
   ```

3. **Run the server**:
   ```bash
   uvicorn app.main:app --reload --port 8002
   ```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and API endpoints
│   ├── config.py            # Centralized configuration (CUSTOMIZE THIS)
│   ├── assistant_agent.py   # AI agent configuration
│   ├── documents.py         # Document metadata (auto-generated)
│   └── memory_store.py      # Store implementation (replace for production)
├── data/                    # Document files for preview
├── pyproject.toml           # Python dependencies
└── README.md
```

## Customization

### 1. Configuration (config.py)

Update `app/config.py` or set environment variables:

- `ASSISTANT_NAME` - Name of your chatbot
- `ASSISTANT_INSTRUCTIONS_TEMPLATE` - Behavior and response style
- `ASSISTANT_MODEL` - AI model (gpt-4.1-mini, gpt-4o, etc.)
- `ASSISTANT_TEMPERATURE` - Response creativity (0.0-1.0)
- `MAX_SEARCH_RESULTS` - Document chunks to retrieve

### 2. Documents

Add documents to knowledge base:

```bash
# 1. Place document files in data/ directory
cp /path/to/docs/*.pdf data/

# 2. Run setup script to upload and configure
cd ..
python scripts/setup-vector-store.py

# This will:
# - Upload documents to OpenAI Vector Store
# - Generate app/documents.py with metadata
# - Update .env with VECTOR_STORE_ID
```

### 3. Production Store

Replace `MemoryStore` with database-backed store:

1. Create a class that implements `Store[dict[str, Any]]`
2. Use PostgreSQL, MongoDB, or Redis for persistence
3. Add authentication/authorization in context checks
4. Update `KnowledgeAssistantServer.__init__()` in main.py

## API Endpoints

- `POST /knowledge/chatkit` - ChatKit protocol (streaming)
- `GET /knowledge/documents` - List all documents
- `GET /knowledge/documents/{id}/file` - Serve document file
- `GET /knowledge/threads/{id}/citations` - Get citations
- `GET /knowledge/health` - Health check

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run linting
ruff check app/

# Run type checking
mypy app/

# Format code
ruff format app/
```

## Deployment

See ../README.md for deployment instructions.

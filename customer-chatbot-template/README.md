# Customer Chatbot Template

A production-ready, customizable template for building ChatKit-powered knowledge assistants. Perfect for creating customer-specific chatbots that can query and cite documents.

## 🚀 Quick Start (30 minutes to deployment)

### 1. Initial Setup

```bash
# Clone or copy this template
cp -r customer-chatbot-template/ my-customer-chatbot/
cd my-customer-chatbot/

# Install dependencies
npm install  # For concurrently
cd backend && pip install -e .  # Python backend
cd ../frontend && npm install   # React frontend
cd ..
```

### 2. Configuration

**Option A: Interactive (Recommended)**
```bash
python scripts/configure-customer.py
```

**Option B: Manual**
```bash
# Copy environment template
cp .env.template .env

# Edit .env and fill in:
# - OPENAI_API_KEY (required)
# - ASSISTANT_NAME (your chatbot name)
# - Other customization options
```

### 3. Add Documents

```bash
# Place your documents in backend/data/
cp /path/to/customer/docs/*.pdf backend/data/

# Upload to OpenAI Vector Store and generate metadata
python scripts/setup-vector-store.py
```

This will:
- ✅ Upload documents to OpenAI Vector Store
- ✅ Generate `backend/app/documents.py` with metadata
- ✅ Update `.env` with `VECTOR_STORE_ID`

### 4. Start Development

```bash
# Start both backend and frontend
npm start

# Or start individually:
npm run backend   # http://localhost:8002
npm run frontend  # http://localhost:5172
```

### 5. Customize (Optional)

- **Behavior**: Edit `backend/app/config.py` (instructions, model, temperature)
- **Branding**: Edit frontend files in `frontend/src/`
- **Documents**: Add/remove files in `backend/data/` and re-run setup script

---

## 📁 Project Structure

```
customer-chatbot-template/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app + ChatKit server
│   │   ├── config.py          # 🎯 MAIN CUSTOMIZATION FILE
│   │   ├── assistant_agent.py # AI agent configuration
│   │   ├── documents.py       # Document metadata (auto-generated)
│   │   └── memory_store.py    # In-memory store (replace for production)
│   ├── data/                  # 📄 Put customer documents here
│   └── pyproject.toml         # Python dependencies
│
├── frontend/                  # React + Vite frontend (OPTIONAL - create if needed)
│   ├── src/
│   │   ├── components/        # React components
│   │   └── lib/config.ts      # Frontend configuration
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/
│   ├── setup-vector-store.py  # 🔧 Document upload automation
│   └── configure-customer.py  # 🔧 Interactive configuration
│
├── .env.template              # Environment variable template
├── .env                       # Your configuration (git-ignored)
├── package.json               # Root orchestration
└── README.md                  # This file
```

---

## 🎨 Customization Guide

### Backend Customization

#### 1. **config.py** - Main Configuration File

```python
# backend/app/config.py

# Change assistant name
ASSISTANT_NAME = "Acme Corp Knowledge Assistant"

# Customize instructions (how the bot behaves)
ASSISTANT_INSTRUCTIONS_TEMPLATE = """
You are a **{assistant_name}** specializing in [YOUR DOMAIN].

Your task:
- Always search documents before responding
- Provide 2-4 sentence answers with citations
- Use format: (filename, page)
- List sources at the end

[ADD YOUR CUSTOM RULES HERE]
"""

# Choose AI model
ASSISTANT_MODEL = "gpt-4o"  # or "gpt-4.1-mini", "gpt-4o-mini"

# Response creativity
ASSISTANT_TEMPERATURE = 0.2  # Lower = more consistent
```

#### 2. **Documents** - Knowledge Base

```bash
# Add documents
cp /path/to/docs/*.pdf backend/data/

# Re-upload and regenerate metadata
python scripts/setup-vector-store.py

# Or update metadata only (no re-upload)
python scripts/setup-vector-store.py --update-only
```

Supported formats: PDF, HTML, TXT, MD, DOCX

#### 3. **Store** - Persistence (Production)

Replace `MemoryStore` with database-backed implementation:

```python
# backend/app/main.py

from your_db_store import PostgresStore

class KnowledgeAssistantServer(ChatKitServer[dict[str, Any]]):
    def __init__(self, agent: Agent[AgentContext]) -> None:
        self.store = PostgresStore(database_url=os.getenv("DATABASE_URL"))
        # ... rest of implementation
```

See `backend/app/memory_store.py` for interface and production TODO comments.

### Frontend Customization (If Using)

#### 1. **Branding** - Colors & Text

```typescript
// frontend/src/lib/config.ts

export const KNOWLEDGE_GREETING = "Welcome to Acme Corp Assistant!"
export const KNOWLEDGE_STARTER_PROMPTS = [
  "What are our refund policies?",
  "How do I submit an expense report?",
  "Tell me about our benefits package"
]

// ChatKit theme
theme: {
  color: { primary: "#your-brand-color" },
  radius: "round"
}
```

#### 2. **Custom Components**

Replace or extend components in `frontend/src/components/`:
- `Home.tsx` - Main layout
- `ChatKitPanel.tsx` - Chat interface
- `KnowledgeDocumentsPanel.tsx` - Document list with citations

---

## 🔧 Advanced Features

### Multi-Customer Deployment

Serve multiple customers from one codebase:

```bash
# Create customer-specific env files
cp .env .env.customer-a
cp .env .env.customer-b

# Edit each file with customer-specific settings
# - Different VECTOR_STORE_ID
# - Different ASSISTANT_NAME
# - Different branding

# Start with specific config
ENV_FILE=.env.customer-a npm run backend
```

### Custom API Endpoints

Add endpoints in `backend/app/main.py`:

```python
@app.get("/knowledge/custom-endpoint")
async def custom_endpoint() -> dict[str, Any]:
    # Your custom logic
    return {"data": "..."}
```

### Authentication

Add auth middleware:

```python
# backend/app/main.py

from your_auth import AuthMiddleware

app.add_middleware(AuthMiddleware)

# Use context in store methods
async def load_thread(self, thread_id: str, context: dict[str, Any]):
    user_id = context.get("user_id")
    # Verify user owns this thread
    ...
```

### Analytics & Monitoring

```python
# backend/app/main.py

from your_analytics import track_event

class KnowledgeAssistantServer(ChatKitServer):
    async def respond(self, thread, item, context):
        track_event("message_received", user_id=context.get("user_id"))
        async for event in stream_agent_response(...):
            yield event
        track_event("response_complete")
```

---

## 📊 Production Deployment

### 1. Environment Setup

```bash
# Production .env
OPENAI_API_KEY=sk-proj-production-key
VECTOR_STORE_ID=vs_production_store
ASSISTANT_NAME="Customer Production Bot"
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING

# Database for persistence
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional: Redis for caching
REDIS_URL=redis://host:6379
```

### 2. Docker Deployment (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy backend
COPY backend/ ./backend/
RUN pip install -e ./backend

# Copy frontend build (if using)
COPY frontend/dist/ ./frontend/dist/

# Environment
COPY .env .env

EXPOSE 8002

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

Build and run:

```bash
docker build -t customer-chatbot .
docker run -p 8002:8002 --env-file .env customer-chatbot
```

### 3. Cloud Deployment

**AWS**:
- ECS/Fargate for containers
- RDS for PostgreSQL store
- S3 for document storage
- CloudFront for frontend

**Azure**:
- App Service for backend
- Azure Database for PostgreSQL
- Blob Storage for documents
- CDN for frontend

**GCP**:
- Cloud Run for containers
- Cloud SQL for PostgreSQL
- Cloud Storage for documents
- Cloud CDN for frontend

### 4. Monitoring

```python
# Add to backend/app/main.py

import sentry_sdk

sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

# Or use OpenTelemetry, DataDog, etc.
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:e2e
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Replace `MemoryStore` with authenticated database store
- [ ] Set `CORS_ORIGINS` to your specific domain (not `*`)
- [ ] Enable HTTPS/SSL for all endpoints
- [ ] Add rate limiting middleware
- [ ] Implement user authentication
- [ ] Sanitize file uploads (if enabled)
- [ ] Set up logging and monitoring
- [ ] Rotate API keys regularly
- [ ] Review and test authorization logic in Store methods
- [ ] Enable CSP headers for frontend
- [ ] Set up automated backups for database
- [ ] Implement request validation and input sanitization

---

## 📚 Documentation & Support

### Key Files to Review

1. **`backend/app/config.py`** - All configuration options with comments
2. **`backend/app/main.py`** - Extensive inline documentation
3. **`backend/app/memory_store.py`** - Production TODOs and interface
4. **`scripts/setup-vector-store.py`** - Document upload process

### OpenAI Resources

- [ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [Agents SDK](https://platform.openai.com/docs/agents)
- [Vector Stores](https://platform.openai.com/docs/vector-stores)
- [File Search](https://platform.openai.com/docs/assistants/tools/file-search)

### Common Issues

**"VECTOR_STORE_ID not set"**
- Run `python scripts/setup-vector-store.py`
- Or set manually in `.env`

**"Documents not found"**
- Ensure files are in `backend/data/`
- Re-run setup script after adding files

**"No citations returned"**
- Check document filename matching in `documents.py`
- Review agent instructions for citation format
- Verify files uploaded to correct vector store

**CORS errors**
- Update `CORS_ORIGINS` in `.env`
- Check frontend proxy configuration in `vite.config.ts`

---

## 🎯 Example Use Cases

This template works great for:

- 📘 **Internal Knowledge Bases** - Employee documentation, policies, procedures
- 📄 **Legal Document Q&A** - Contracts, compliance docs, regulations
- 🏥 **Medical Information** - Treatment protocols, research papers
- 🏗️ **Technical Documentation** - API docs, architecture guides
- 📊 **Financial Reports** - Quarterly reports, analyst presentations
- 🎓 **Educational Content** - Course materials, research papers
- 🏪 **Customer Support** - Product manuals, FAQs, troubleshooting guides

---

## 📝 License

This template is provided as-is for customer projects. Customize freely for your use cases.

---

## 🤝 Contributing

Improvements welcome! Common enhancements:

- Additional store implementations (PostgreSQL, MongoDB, Redis)
- Authentication examples (OAuth, JWT)
- Deployment scripts for various clouds
- Example frontend customizations
- Testing utilities

---

## ✅ Deployment Checklist

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for step-by-step production deployment guide.

---

**Ready to get started? Run:**

```bash
python scripts/configure-customer.py
```

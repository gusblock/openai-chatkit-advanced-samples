# Quick Start Guide

Get your customer chatbot running in 5 minutes.

## Prerequisites

- Python 3.11+ installed
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Customer documents (PDF, HTML, TXT, MD, or DOCX files)

## 5-Minute Setup

### Step 1: Configure (2 minutes)

```bash
# Interactive configuration wizard
python scripts/configure-customer.py
```

Or manually:

```bash
# Copy template
cp .env.template .env

# Edit .env and set at minimum:
# OPENAI_API_KEY=sk-proj-your-key-here
# ASSISTANT_NAME=Your Bot Name
```

### Step 2: Add Documents (1 minute)

```bash
# Copy your customer's documents
cp /path/to/customer/docs/*.pdf backend/data/

# Upload to OpenAI and generate metadata
python scripts/setup-vector-store.py
```

### Step 3: Install & Run (2 minutes)

```bash
# Install backend dependencies
cd backend
pip install -e .

# Start the backend server
uvicorn app.main:app --reload --port 8002
```

That's it! Your chatbot is running at `http://localhost:8002`

## Test It

```bash
# Health check
curl http://localhost:8002/knowledge/health

# List documents
curl http://localhost:8002/knowledge/documents

# Chat (via frontend or API)
# Open your frontend at http://localhost:5172 (if using)
# Or integrate with your own UI using the ChatKit protocol
```

## Next Steps

1. **Customize behavior**: Edit `backend/app/config.py`
2. **Add frontend**: Copy from the original knowledge-assistant example or build your own
3. **Deploy**: See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## Common First-Time Issues

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY=sk-proj-your-key
```

### "VECTOR_STORE_ID not set"
```bash
python scripts/setup-vector-store.py
```

### "No documents found"
```bash
# Add files to backend/data/
cp /path/to/docs/*.pdf backend/data/
# Then re-run setup
python scripts/setup-vector-store.py
```

## Full Documentation

- [README.md](README.md) - Complete guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Production deployment
- [backend/app/config.py](backend/app/config.py) - Configuration options
- [backend/README.md](backend/README.md) - Backend details

## Help

Need help? Check:
1. Logs: Look at terminal output for errors
2. Configuration: Review `backend/app/config.py`
3. Documentation: Read inline comments in code files
4. OpenAI Status: https://status.openai.com/

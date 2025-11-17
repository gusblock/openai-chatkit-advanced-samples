# Customer Chatbot Template - Overview

## What Is This?

A production-ready, reusable template for building ChatKit-powered knowledge assistants. Designed to be copied and customized for different customer projects, allowing you to deploy chatbots that can intelligently query and cite documents in 30 minutes.

## Key Features

### 🎯 Ready for Customization
- **Centralized Configuration**: All settings in one place (`config.py` and `.env`)
- **Automated Setup**: Scripts handle document upload and configuration
- **Well Documented**: Extensive inline comments and documentation
- **Production Ready**: Security TODOs, deployment checklist, and best practices

### 🤖 Powered by OpenAI
- **ChatKit Protocol**: Built-in streaming chat interface
- **Agents SDK**: Intelligent agent with File Search tool
- **Vector Store**: Semantic document search and retrieval
- **Citation Support**: Automatic source attribution

### 🔧 Customization Points

1. **Assistant Behavior** (`backend/app/config.py`)
   - Name and personality
   - Response style and instructions
   - AI model selection
   - Temperature and creativity settings

2. **Document Knowledge Base**
   - Upload any PDF, HTML, TXT, MD, DOCX files
   - Automatic metadata generation
   - Citation tracking and display

3. **Frontend Branding** (if using frontend)
   - Welcome messages
   - Starter prompts
   - Colors and themes
   - Custom components

4. **Production Features**
   - Authentication (TODOs provided)
   - Database persistence (interface ready)
   - Monitoring and logging
   - Multi-customer deployment

## What's Included

### Backend Components

```
backend/
├── app/
│   ├── config.py           ⭐ Main configuration file
│   ├── main.py             📡 FastAPI app + ChatKit server
│   ├── assistant_agent.py  🤖 AI agent definition
│   ├── documents.py        📚 Document metadata (auto-generated)
│   └── memory_store.py     💾 Store implementation (replace for prod)
├── data/                   📄 Customer documents
└── pyproject.toml          📦 Dependencies
```

**Key Files:**
- **[config.py](backend/app/config.py)** - Single source of truth for all configuration
- **[main.py](backend/app/main.py)** - Heavily documented ChatKit server implementation
- **[memory_store.py](backend/app/memory_store.py)** - Store interface with production TODOs

### Automation Scripts

```
scripts/
├── setup-vector-store.py   🔧 Upload docs + generate metadata
└── configure-customer.py   ⚙️ Interactive configuration wizard
```

**Features:**
- Automatic document upload to OpenAI Vector Store
- Metadata generation from filenames
- Environment variable management
- Interactive setup wizard

### Documentation

```
├── README.md                    📖 Complete guide
├── QUICKSTART.md               ⚡ 5-minute setup
├── DEPLOYMENT_CHECKLIST.md     ✅ Production deployment
├── TEMPLATE_OVERVIEW.md        📋 This file
└── backend/README.md           🔧 Backend details
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Frontend                         │
│            (Optional - build your own or use                 │
│             the knowledge-assistant example)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/SSE
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         KnowledgeAssistantServer                     │   │
│  │         (ChatKitServer Implementation)               │   │
│  └──────────────────────────────────────────────────────┘   │
│           │                │                  │              │
│  ┌────────┴────┐  ┌────────┴────────┐  ┌─────┴──────┐      │
│  │MemoryStore  │  │ assistant_agent │  │ config.py  │      │
│  │(or your DB) │  │                 │  │            │      │
│  └─────────────┘  └─────────────────┘  └────────────┘      │
│                           │                                 │
│                  ┌────────┴─────────┐                       │
│                  │  OpenAI Services  │                       │
│                  │  - Vector Store   │                       │
│                  │  - File Search    │                       │
│                  │  - GPT Models     │                       │
│                  └───────────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Typical Workflow

### For Each New Customer

1. **Copy Template**
   ```bash
   cp -r customer-chatbot-template/ acme-corp-bot/
   cd acme-corp-bot/
   ```

2. **Configure**
   ```bash
   python scripts/configure-customer.py
   # Or manually edit .env
   ```

3. **Add Documents**
   ```bash
   cp /path/to/acme/docs/*.pdf backend/data/
   python scripts/setup-vector-store.py
   ```

4. **Customize**
   - Edit `backend/app/config.py` for behavior
   - Edit `.env` for settings
   - Customize frontend if using

5. **Deploy**
   - Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
   - Or start locally: `npm start`

**Time Required:** 30-60 minutes per customer

## What You Need to Provide

### Required

1. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Will be used for API calls (you pay based on usage)

2. **Customer Documents**
   - Supported: PDF, HTML, TXT, MD, DOCX
   - Place in `backend/data/`
   - Automatically uploaded to Vector Store

3. **Customer Information**
   - Company name / project name
   - Desired chatbot behavior
   - Any specific requirements

### Optional

1. **Frontend**
   - Can use the knowledge-assistant frontend example
   - Or build your own using ChatKit React library
   - Or integrate into existing app

2. **Database**
   - For production, replace MemoryStore
   - PostgreSQL, MongoDB, or Redis recommended
   - Interface already defined in `memory_store.py`

3. **Authentication**
   - Add if needed for multi-user scenarios
   - TODOs provided in code comments
   - Use JWT, OAuth, or session-based

## Customization Examples

### Example 1: Legal Document Assistant

```python
# backend/app/config.py

ASSISTANT_NAME = "Legal Document Assistant"

ASSISTANT_INSTRUCTIONS_TEMPLATE = """
You are a **Legal Document Assistant** specializing in contract review.

Your task:
- Always search legal documents before responding
- Provide precise, conservative answers
- Include exact citations with section numbers
- Never provide legal advice - only factual information from documents
- Flag when information is not found in the knowledge base

Limit responses to 2-3 sentences with sources.
"""

ASSISTANT_TEMPERATURE = 0.0  # Maximum consistency for legal
```

### Example 2: Technical Documentation Bot

```python
# backend/app/config.py

ASSISTANT_NAME = "TechDocs Assistant"

ASSISTANT_INSTRUCTIONS_TEMPLATE = """
You are a **Technical Documentation Assistant** for our API platform.

Your task:
- Search documentation before responding
- Provide code examples when available
- Include links to relevant sections
- Use technical terminology accurately
- Suggest related topics when relevant

Keep answers clear and concise (2-4 sentences) with citations.
"""

ASSISTANT_MODEL = "gpt-4o"  # More capable for code
MAX_SEARCH_RESULTS = 8  # More context for technical answers
```

### Example 3: Customer Support Bot

```python
# backend/app/config.py

ASSISTANT_NAME = "Acme Support Assistant"

ASSISTANT_INSTRUCTIONS_TEMPLATE = """
You are a **Customer Support Assistant** for Acme Corp.

Your task:
- Search product manuals and FAQs
- Provide friendly, helpful responses
- Include step-by-step instructions when applicable
- Cite relevant documentation
- Suggest escalation to human support when needed

Keep tone friendly and conversational (3-4 sentences) with sources.
"""

ASSISTANT_TEMPERATURE = 0.4  # Slightly more natural language
```

## Migration from Original Example

If you have code based on the original knowledge-assistant example:

1. **Configuration**: Move settings from hardcoded values to `config.py`
2. **Documents**: Run setup script instead of manual upload
3. **Environment**: Use `.env` file for all configuration
4. **Store**: Use provided MemoryStore or implement your own
5. **Frontend**: Can reuse as-is or customize

## Production Considerations

### Must Do

- [ ] Replace `MemoryStore` with database store
- [ ] Add authentication/authorization
- [ ] Set proper CORS origins
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Set up monitoring

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for complete list.

### Should Do

- [ ] Add caching (Redis)
- [ ] Implement analytics
- [ ] Add automated backups
- [ ] Set up CI/CD pipeline
- [ ] Create admin dashboard

### Nice to Have

- [ ] Multi-language support
- [ ] Custom analytics
- [ ] A/B testing for responses
- [ ] User feedback collection

## Cost Estimation

Costs depend on usage and configuration:

### OpenAI API Costs

**Vector Store:**
- Storage: ~$0.10/GB/day
- Typical 100 documents: ~$0.50/month

**Chat Completions (GPT-4.1-mini):**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Typical conversation: 1000 tokens = $0.0007

**Estimated Monthly Costs:**
- 1,000 messages/month: ~$1-5
- 10,000 messages/month: ~$10-50
- 100,000 messages/month: ~$100-500

**To Reduce Costs:**
- Use `gpt-4.1-mini` (cheapest)
- Lower `MAX_SEARCH_RESULTS`
- Cache common queries
- Set lower `ASSISTANT_TEMPERATURE`

## Support & Resources

### Documentation

- **This Template**: Inline comments in all files
- **ChatKit**: https://platform.openai.com/docs/chatkit
- **Agents SDK**: https://platform.openai.com/docs/agents
- **Vector Stores**: https://platform.openai.com/docs/vector-stores

### Community

- OpenAI Developer Forum
- ChatKit GitHub Issues
- Stack Overflow (tag: openai-chatkit)

## Version History

- **v1.0.0** (2024) - Initial template release
  - Centralized configuration
  - Automation scripts
  - Comprehensive documentation
  - Production-ready structure

## License

This template is provided for customer projects. Customize and deploy as needed for your use cases.

---

**Ready to start?** See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

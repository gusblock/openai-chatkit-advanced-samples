"""
Centralized configuration for the customer chatbot.

CUSTOMIZATION INSTRUCTIONS:
- Update these values for each customer deployment
- All configuration is driven by environment variables with sensible defaults
- For production: Set these via .env file or deployment environment
"""
from __future__ import annotations

import os
from pathlib import Path

# ==============================================================================
# OPENAI CONFIGURATION
# ==============================================================================

# Required: Your OpenAI API key
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY environment variable is required. "
        "Set it in your .env file or environment."
    )

# Required: Vector Store ID containing your customer's documents
# Create via: python scripts/setup-vector-store.py
# Or manually at: https://platform.openai.com/storage
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")
if not VECTOR_STORE_ID:
    raise RuntimeError(
        "VECTOR_STORE_ID environment variable is required. "
        "Run 'python scripts/setup-vector-store.py' to create one."
    )

# ==============================================================================
# ASSISTANT CONFIGURATION
# ==============================================================================

# CUSTOMIZE: The name of your AI assistant
# Example: "Acme Corp Knowledge Assistant", "Legal Document Helper"
ASSISTANT_NAME = os.getenv(
    "ASSISTANT_NAME",
    "Knowledge Assistant"  # Default name
)

# CUSTOMIZE: The AI model to use
# Options: "gpt-4.1-mini" (fast, cheap), "gpt-4o" (more capable), "gpt-4o-mini" (balanced)
ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "gpt-4.1-mini")

# CUSTOMIZE: Response creativity (0.0 = deterministic, 1.0 = creative)
# For factual knowledge bases, keep low (0.0-0.3)
# For creative applications, increase (0.5-0.9)
ASSISTANT_TEMPERATURE = float(os.getenv("ASSISTANT_TEMPERATURE", "0.3"))

# CUSTOMIZE: Maximum number of document chunks to retrieve per query
# Higher = more context but slower and more expensive
# Recommended: 3-10
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

# ==============================================================================
# ASSISTANT INSTRUCTIONS
# ==============================================================================

# CUSTOMIZE: These instructions define how your assistant behaves
# Modify this template for your specific domain and requirements
ASSISTANT_INSTRUCTIONS_TEMPLATE = """
You are a **{assistant_name}**.

**Your task**
- Always call the `file_search` tool before responding. Use the passages it returns as your evidence.
- Compose a concise answer (2–4 sentences) grounded **only** in the retrieved passages.
- Every factual sentence must include a citation in the format `(filename, page/section)`.
  If you cannot provide such a citation, say "I don't see that in the knowledge base." instead of guessing.
- After the answer, optionally list key supporting bullets—each bullet needs its own citation.
- Finish with a `Sources:` section listing each supporting document on its own line: `- filename (page/section)`.
  Do not omit this section even if there is only one source.

**Interaction guardrails**
1. Ask for clarification when the question is ambiguous.
2. Explain when the knowledge base does not contain the requested information.
3. Never rely on external knowledge or unstated assumptions.
4. Be helpful, professional, and concise.

Limit the entire response with citations to 2-4 sentences.
""".strip()

# Generate the final instructions by substituting variables
ASSISTANT_INSTRUCTIONS = ASSISTANT_INSTRUCTIONS_TEMPLATE.format(
    assistant_name=ASSISTANT_NAME
)

# ==============================================================================
# SERVER CONFIGURATION
# ==============================================================================

# Server host and port
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))

# CORS settings (for production, restrict to your frontend domain)
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ==============================================================================
# FILE PATHS
# ==============================================================================

# Base paths
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# LOGGING
# ==============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

__all__ = [
    "OPENAI_API_KEY",
    "VECTOR_STORE_ID",
    "ASSISTANT_NAME",
    "ASSISTANT_MODEL",
    "ASSISTANT_TEMPERATURE",
    "ASSISTANT_INSTRUCTIONS",
    "MAX_SEARCH_RESULTS",
    "SERVER_HOST",
    "SERVER_PORT",
    "CORS_ORIGINS",
    "DATA_DIR",
    "LOG_LEVEL",
]

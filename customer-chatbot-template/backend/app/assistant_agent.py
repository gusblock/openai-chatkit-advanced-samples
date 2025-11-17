"""
AI Assistant Agent Configuration

This module defines the AI agent that powers your chatbot.
The agent uses OpenAI's Agents SDK with the File Search tool for retrieval-augmented generation.

CUSTOMIZATION POINTS:
1. config.ASSISTANT_INSTRUCTIONS - Define how the assistant behaves
2. config.ASSISTANT_MODEL - Choose the AI model (gpt-4.1-mini, gpt-4o, etc.)
3. config.ASSISTANT_NAME - Give your assistant a custom name
4. config.MAX_SEARCH_RESULTS - Control how many document chunks are retrieved
"""
from __future__ import annotations

from agents import Agent
from agents.models.openai_responses import FileSearchTool
from chatkit.agents import AgentContext

from .config import (
    ASSISTANT_INSTRUCTIONS,
    ASSISTANT_MODEL,
    ASSISTANT_NAME,
    MAX_SEARCH_RESULTS,
    VECTOR_STORE_ID,
)


def build_file_search_tool() -> FileSearchTool:
    """
    Creates the File Search tool that enables the assistant to retrieve
    relevant information from your document vector store.

    The File Search tool:
    - Searches through documents uploaded to your OpenAI Vector Store
    - Returns the most relevant chunks based on semantic similarity
    - Provides page/section references for citations

    Returns:
        FileSearchTool configured with your vector store

    Raises:
        RuntimeError: If VECTOR_STORE_ID is not set in config
    """
    if not VECTOR_STORE_ID:
        raise RuntimeError(
            "VECTOR_STORE_ID is not configured. "
            "Run 'python scripts/setup-vector-store.py' to create a vector store, "
            "then set VECTOR_STORE_ID in your .env file."
        )

    return FileSearchTool(
        vector_store_ids=[VECTOR_STORE_ID],
        max_num_results=MAX_SEARCH_RESULTS,
    )


# ==============================================================================
# MAIN ASSISTANT AGENT
# ==============================================================================

assistant_agent = Agent[AgentContext](
    model=ASSISTANT_MODEL,
    name=ASSISTANT_NAME,
    instructions=ASSISTANT_INSTRUCTIONS,
    tools=[build_file_search_tool()],
)

"""
The assistant_agent is the core of your chatbot.

It combines:
- A language model (GPT-4.1-mini by default) for response generation
- File Search tool for retrieving relevant document chunks
- Custom instructions that enforce citation behavior and response style

The agent will:
1. Receive user questions
2. Search the vector store for relevant information
3. Generate responses grounded in the retrieved documents
4. Include citations to source documents
"""

__all__ = [
    "assistant_agent",
    "build_file_search_tool",
]

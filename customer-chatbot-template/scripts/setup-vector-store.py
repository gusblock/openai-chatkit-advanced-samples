#!/usr/bin/env python3
"""
Vector Store Setup Script

This script automates the process of:
1. Creating an OpenAI Vector Store
2. Uploading documents from backend/data/ directory
3. Generating backend/app/documents.py with metadata
4. Updating .env file with VECTOR_STORE_ID

Usage:
    python scripts/setup-vector-store.py

Environment Variables Required:
    OPENAI_API_KEY - Your OpenAI API key

Options:
    --data-dir PATH     - Path to documents directory (default: backend/data)
    --assistant-name    - Name for the vector store (default: from config or prompt)
    --update-only       - Only regenerate documents.py from existing vector store
    --vector-store-id   - Use existing vector store ID (skip creation)
"""

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed")
    print("Install with: pip install openai")
    sys.exit(1)


@dataclass
class DocumentInfo:
    """Information about an uploaded document."""
    file_id: str
    filename: str
    title: str
    description: str


def slugify(text: str) -> str:
    """Convert text to a valid Python identifier."""
    # Remove extension
    text = Path(text).stem
    # Remove number prefixes like "01_"
    if text and text[0].isdigit():
        parts = text.split("_", 1)
        if len(parts) > 1:
            text = parts[1]
    # Replace non-alphanumeric with underscore
    slug = "".join(c if c.isalnum() else "_" for c in text)
    # Remove consecutive underscores
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_").lower()


def generate_title(filename: str) -> str:
    """Generate a human-readable title from filename."""
    stem = Path(filename).stem
    # Remove number prefixes
    if stem and stem[0].isdigit():
        parts = stem.split("_", 1)
        if len(parts) > 1:
            stem = parts[1]
    # Replace underscores and hyphens with spaces, title case
    title = stem.replace("_", " ").replace("-", " ").title()
    return title


def collect_documents(data_dir: Path) -> List[Path]:
    """
    Collect document files from the data directory.

    Supported formats: PDF, HTML, TXT, MD, DOCX
    """
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print(f"Create it and add your documents: mkdir -p {data_dir}")
        sys.exit(1)

    supported_extensions = {".pdf", ".html", ".txt", ".md", ".docx", ".doc"}
    documents = [
        f for f in sorted(data_dir.iterdir())
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not documents:
        print(f"Error: No documents found in {data_dir}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        sys.exit(1)

    return documents


def upload_documents(client: OpenAI, documents: List[Path]) -> List[DocumentInfo]:
    """Upload documents to OpenAI and return file information."""
    print(f"\n📤 Uploading {len(documents)} documents to OpenAI...")

    uploaded = []
    for doc_path in documents:
        print(f"  Uploading {doc_path.name}...", end=" ", flush=True)
        try:
            with open(doc_path, "rb") as f:
                file_obj = client.files.create(file=f, purpose="assistants")

            uploaded.append(
                DocumentInfo(
                    file_id=file_obj.id,
                    filename=doc_path.name,
                    title=generate_title(doc_path.name),
                    description=f"Knowledge base document: {generate_title(doc_path.name)}",
                )
            )
            print(f"✓ ({file_obj.id})")
        except Exception as e:
            print(f"✗ Failed: {e}")
            # Continue with other files

    if not uploaded:
        print("Error: No documents uploaded successfully")
        sys.exit(1)

    return uploaded


def create_vector_store(
    client: OpenAI, documents: List[DocumentInfo], store_name: str
) -> str:
    """Create a vector store and add documents to it."""
    print(f"\n🗄️  Creating vector store '{store_name}'...")

    try:
        vector_store = client.beta.vector_stores.create(
            name=store_name,
            file_ids=[doc.file_id for doc in documents],
        )
        print(f"✓ Vector store created: {vector_store.id}")
        return vector_store.id

    except Exception as e:
        print(f"✗ Failed to create vector store: {e}")
        sys.exit(1)


def generate_documents_py(documents: List[DocumentInfo], output_path: Path) -> None:
    """Generate documents.py file with document metadata."""
    print(f"\n📝 Generating {output_path}...")

    # Build document entries
    doc_entries = []
    for doc in documents:
        slug = slugify(doc.filename)
        doc_entries.append(
            f'''    DocumentMetadata(
        id="{slug}",
        filename="{doc.filename}",
        title="{doc.title}",
        description="{doc.description}",
    ),'''
        )

    documents_tuple = "\n".join(doc_entries)

    content = f'''"""
Document Metadata Registry

This file was AUTO-GENERATED by scripts/setup-vector-store.py
Last generated: {Path(__file__).stat().st_mtime}

Do not edit manually - run the setup script again to regenerate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


def _normalise(value: str) -> str:
    """Normalize string for matching (lowercase, trimmed)."""
    return value.strip().lower()


def _slugify(value: str) -> str:
    """Convert string to alphanumeric-only slug for fuzzy matching."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    """
    Metadata for a single document in the knowledge base.

    Attributes:
        id: Unique identifier (used in API responses)
        filename: Exact filename as uploaded to Vector Store
        title: Human-readable title (displayed in UI)
        description: Brief description of document contents
    """
    id: str
    filename: str
    title: str
    description: str | None = None

    @property
    def stem(self) -> str:
        """Filename without extension."""
        return Path(self.filename).stem


# ==============================================================================
# DOCUMENT REGISTRY - {len(documents)} documents
# ==============================================================================

DOCUMENTS: tuple[DocumentMetadata, ...] = (
{documents_tuple}
)

# ==============================================================================
# DOCUMENT LOOKUP INDICES
# ==============================================================================

DOCUMENTS_BY_ID: dict[str, DocumentMetadata] = {{
    doc.id: doc for doc in DOCUMENTS
}}

DOCUMENTS_BY_FILENAME: dict[str, DocumentMetadata] = {{
    _normalise(doc.filename): doc for doc in DOCUMENTS
}}

DOCUMENTS_BY_STEM: dict[str, DocumentMetadata] = {{
    _normalise(doc.stem): doc for doc in DOCUMENTS
}}

DOCUMENTS_BY_SLUG: dict[str, DocumentMetadata] = {{}}
for document in DOCUMENTS:
    for candidate in {{
        document.id,
        document.filename,
        document.stem,
        document.title,
        document.description or "",
    }}:
        if candidate:
            DOCUMENTS_BY_SLUG.setdefault(_slugify(candidate), document)


def as_dicts(documents: Iterable[DocumentMetadata]) -> list[dict[str, str | None]]:
    """Convert document metadata objects to dictionaries for JSON serialization."""
    return [asdict(document) for document in documents]


def find_document(query: str) -> DocumentMetadata | None:
    """Find a document by ID, filename, or fuzzy match."""
    if query in DOCUMENTS_BY_ID:
        return DOCUMENTS_BY_ID[query]
    normalized = _normalise(query)
    if normalized in DOCUMENTS_BY_FILENAME:
        return DOCUMENTS_BY_FILENAME[normalized]
    if normalized in DOCUMENTS_BY_STEM:
        return DOCUMENTS_BY_STEM[normalized]
    slug = _slugify(query)
    if slug in DOCUMENTS_BY_SLUG:
        return DOCUMENTS_BY_SLUG[slug]
    return None


__all__ = [
    "DOCUMENTS",
    "DOCUMENTS_BY_FILENAME",
    "DOCUMENTS_BY_ID",
    "DOCUMENTS_BY_STEM",
    "DOCUMENTS_BY_SLUG",
    "DocumentMetadata",
    "as_dicts",
    "find_document",
]
'''

    output_path.write_text(content)
    print(f"✓ Generated with {len(documents)} documents")


def update_env_file(env_path: Path, vector_store_id: str) -> None:
    """Update .env file with VECTOR_STORE_ID."""
    print(f"\n⚙️  Updating {env_path}...")

    if env_path.exists():
        # Update existing file
        lines = env_path.read_text().splitlines()
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("VECTOR_STORE_ID="):
                lines[i] = f"VECTOR_STORE_ID={vector_store_id}"
                updated = True
                break

        if not updated:
            lines.append(f"VECTOR_STORE_ID={vector_store_id}")

        env_path.write_text("\n".join(lines) + "\n")
    else:
        # Create new file from template
        env_path.write_text(f"VECTOR_STORE_ID={vector_store_id}\n")

    print(f"✓ Updated VECTOR_STORE_ID={vector_store_id}")


def main():
    parser = argparse.ArgumentParser(description="Setup OpenAI Vector Store for customer chatbot")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent.parent / "backend" / "data",
        help="Path to documents directory",
    )
    parser.add_argument(
        "--assistant-name",
        type=str,
        help="Name for the vector store",
    )
    parser.add_argument(
        "--vector-store-id",
        type=str,
        help="Use existing vector store ID (skip creation)",
    )
    parser.add_argument(
        "--update-only",
        action="store_true",
        help="Only regenerate documents.py from existing files (no upload)",
    )
    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent
    data_dir = args.data_dir.resolve()
    documents_py_path = project_root / "backend" / "app" / "documents.py"
    env_path = project_root / ".env"

    print("🚀 Vector Store Setup")
    print(f"   Data directory: {data_dir}")
    print(f"   Output file: {documents_py_path}")

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and not args.update_only:
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Get your API key from: https://platform.openai.com/api-keys")
        print("   Then set it: export OPENAI_API_KEY=sk-proj-...")
        sys.exit(1)

    # Collect documents
    document_paths = collect_documents(data_dir)
    print(f"\n📄 Found {len(document_paths)} documents:")
    for doc in document_paths:
        print(f"   - {doc.name}")

    if args.update_only:
        # Just regenerate documents.py
        documents = [
            DocumentInfo(
                file_id="",  # Not needed for update-only
                filename=doc.name,
                title=generate_title(doc.name),
                description=f"Knowledge base document: {generate_title(doc.name)}",
            )
            for doc in document_paths
        ]
        generate_documents_py(documents, documents_py_path)
        print("\n✅ Documents metadata updated successfully!")
        return

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Upload documents or use existing vector store
    if args.vector_store_id:
        vector_store_id = args.vector_store_id
        print(f"\n🗄️  Using existing vector store: {vector_store_id}")

        # Still need document info for documents.py
        documents = [
            DocumentInfo(
                file_id="",
                filename=doc.name,
                title=generate_title(doc.name),
                description=f"Knowledge base document: {generate_title(doc.name)}",
            )
            for doc in document_paths
        ]
    else:
        # Upload documents
        documents = upload_documents(client, document_paths)

        # Create vector store
        store_name = args.assistant_name or os.getenv("ASSISTANT_NAME", "Customer Knowledge Base")
        vector_store_id = create_vector_store(client, documents, store_name)

    # Generate documents.py
    generate_documents_py(documents, documents_py_path)

    # Update .env
    update_env_file(env_path, vector_store_id)

    print("\n✅ Setup complete!")
    print(f"\n📋 Next steps:")
    print(f"   1. Review generated file: {documents_py_path}")
    print(f"   2. Customize config in: backend/app/config.py")
    print(f"   3. Start the backend: cd backend && uvicorn app.main:app --reload")
    print(f"\n💡 Vector Store ID: {vector_store_id}")
    print(f"   View at: https://platform.openai.com/storage/vector_stores/{vector_store_id}")


if __name__ == "__main__":
    main()

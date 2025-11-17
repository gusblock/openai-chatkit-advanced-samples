"""
In-Memory Store for ChatKit Threads and Messages

This module provides a simple in-memory implementation of the ChatKit Store interface.
It's suitable for development and demos, but should be replaced with a database-backed
store for production use.

PRODUCTION REPLACEMENT:
For production, replace this with a persistent store implementation using:
- PostgreSQL (recommended for structured data)
- MongoDB (good for document storage)
- Redis (for high-performance caching)

Your production store should:
1. Implement the same Store[dict[str, Any]] interface
2. Add authentication/authorization checks using the 'context' parameter
3. Handle concurrent access safely
4. Persist data across server restarts
5. Implement proper error handling and logging

Example production implementation stubs are included in comments below.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, Thread, ThreadItem, ThreadMetadata


@dataclass
class _ThreadState:
    """Internal representation of a thread with its metadata and items."""
    thread: ThreadMetadata
    items: List[ThreadItem]


class MemoryStore(Store[dict[str, Any]]):
    """
    Simple in-memory store compatible with the ChatKit server interface.

    This store keeps all threads and messages in memory using Python dictionaries.
    Data is lost when the server restarts.

    Attributes:
        _threads: Dictionary mapping thread_id -> _ThreadState

    Context Parameter:
        The 'context' parameter passed to all methods contains request-specific data.
        In production, use this to:
        - Verify user authentication
        - Enforce authorization (user can only access their own threads)
        - Log actions for audit trails
        - Implement rate limiting
    """

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        # Attachments intentionally unsupported; use a real store that enforces auth.

    @staticmethod
    def _coerce_thread_metadata(thread: ThreadMetadata | Thread) -> ThreadMetadata:
        """
        Return thread metadata without any embedded items (openai-chatkit>=1.0).

        ChatKit can pass either ThreadMetadata or Thread objects. This ensures
        we always work with ThreadMetadata (without items embedded).
        """
        has_items = isinstance(thread, Thread) or "items" in getattr(
            thread, "model_fields_set", set()
        )
        if not has_items:
            return thread.model_copy(deep=True)

        data = thread.model_dump()
        data.pop("items", None)
        return ThreadMetadata(**data).model_copy(deep=True)

    # ==========================================================================
    # THREAD METADATA OPERATIONS
    # ==========================================================================

    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata:
        """
        Load metadata for a specific thread.

        Args:
            thread_id: Unique identifier for the thread
            context: Request context (use for auth in production)

        Returns:
            ThreadMetadata for the requested thread

        Raises:
            NotFoundError: If thread doesn't exist

        Production TODO:
            # user_id = context.get("user_id")
            # if not user_id:
            #     raise UnauthorizedError("No user_id in context")
            # thread = await db.query(Thread).filter_by(id=thread_id, user_id=user_id).first()
            # if not thread:
            #     raise NotFoundError(f"Thread {thread_id} not found or not accessible")
        """
        state = self._threads.get(thread_id)
        if not state:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self._coerce_thread_metadata(state.thread)

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        """
        Save or update thread metadata.

        Args:
            thread: Thread metadata to save
            context: Request context (use for auth in production)

        Production TODO:
            # user_id = context.get("user_id")
            # await db.query(Thread).filter_by(id=thread.id).update({
            #     "title": thread.title,
            #     "metadata": thread.metadata,
            #     "updated_at": datetime.utcnow(),
            # })
            # await db.commit()
        """
        metadata = self._coerce_thread_metadata(thread)
        state = self._threads.get(thread.id)
        if state:
            state.thread = metadata
        else:
            self._threads[thread.id] = _ThreadState(
                thread=metadata,
                items=[],
            )

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadMetadata]:
        """
        Load a page of threads for the current user.

        Args:
            limit: Maximum number of threads to return
            after: Cursor for pagination (thread_id to start after)
            order: Sort order ("asc" or "desc" by created_at)
            context: Request context (use for auth in production)

        Returns:
            Page of ThreadMetadata with pagination info

        Production TODO:
            # user_id = context.get("user_id")
            # query = db.query(Thread).filter_by(user_id=user_id)
            # if order == "desc":
            #     query = query.order_by(Thread.created_at.desc())
            # else:
            #     query = query.order_by(Thread.created_at.asc())
            # if after:
            #     after_thread = await db.query(Thread).filter_by(id=after).first()
            #     query = query.filter(Thread.created_at > after_thread.created_at)
            # threads = await query.limit(limit + 1).all()
        """
        threads = sorted(
            (self._coerce_thread_metadata(state.thread) for state in self._threads.values()),
            key=lambda t: t.created_at or datetime.min,
            reverse=(order == "desc"),
        )

        if after:
            index_map = {thread.id: idx for idx, thread in enumerate(threads)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_threads = threads[start : start + limit + 1]
        has_more = len(slice_threads) > limit
        slice_threads = slice_threads[:limit]
        next_after = slice_threads[-1].id if has_more and slice_threads else None
        return Page(
            data=slice_threads,
            has_more=has_more,
            after=next_after,
        )

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        """
        Delete a thread and all its items.

        Args:
            thread_id: ID of thread to delete
            context: Request context (use for auth in production)

        Production TODO:
            # user_id = context.get("user_id")
            # await db.query(ThreadItem).filter_by(thread_id=thread_id).delete()
            # await db.query(Thread).filter_by(id=thread_id, user_id=user_id).delete()
            # await db.commit()
        """
        self._threads.pop(thread_id, None)

    # ==========================================================================
    # THREAD ITEMS (MESSAGES) OPERATIONS
    # ==========================================================================

    def _items(self, thread_id: str) -> List[ThreadItem]:
        """
        Get the list of items for a thread, creating the thread if it doesn't exist.

        This is a helper method for internal use.
        """
        state = self._threads.get(thread_id)
        if state is None:
            state = _ThreadState(
                thread=ThreadMetadata(id=thread_id, created_at=datetime.utcnow()),
                items=[],
            )
            self._threads[thread_id] = state
        return state.items

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        """
        Load a page of items (messages) from a thread.

        Args:
            thread_id: ID of the thread
            after: Cursor for pagination (item_id to start after)
            limit: Maximum number of items to return
            order: Sort order ("asc" or "desc" by created_at)
            context: Request context

        Returns:
            Page of ThreadItem with pagination info

        Production TODO:
            # Verify user has access to this thread
            # Query database with proper indexing for performance
        """
        items = [item.model_copy(deep=True) for item in self._items(thread_id)]
        items.sort(
            key=lambda item: getattr(item, "created_at", datetime.utcnow()),
            reverse=(order == "desc"),
        )

        if after:
            index_map = {item.id: idx for idx, item in enumerate(items)}
            start = index_map.get(after, -1) + 1
        else:
            start = 0

        slice_items = items[start : start + limit + 1]
        has_more = len(slice_items) > limit
        slice_items = slice_items[:limit]
        next_after = slice_items[-1].id if has_more and slice_items else None
        return Page(data=slice_items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict[str, Any]
    ) -> None:
        """
        Add a new item (message) to a thread.

        Args:
            thread_id: ID of the thread
            item: ThreadItem to add
            context: Request context

        Production TODO:
            # await db.add(ThreadItem(**item.model_dump(), thread_id=thread_id))
            # await db.commit()
        """
        self._items(thread_id).append(item.model_copy(deep=True))

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        """
        Save or update an item in a thread.

        If the item exists, it's updated. Otherwise, it's added.

        Args:
            thread_id: ID of the thread
            item: ThreadItem to save
            context: Request context
        """
        items = self._items(thread_id)
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item.model_copy(deep=True)
                return
        items.append(item.model_copy(deep=True))

    async def load_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> ThreadItem:
        """
        Load a specific item from a thread.

        Args:
            thread_id: ID of the thread
            item_id: ID of the item
            context: Request context

        Returns:
            The requested ThreadItem

        Raises:
            NotFoundError: If item doesn't exist
        """
        for item in self._items(thread_id):
            if item.id == item_id:
                return item.model_copy(deep=True)
        raise NotFoundError(f"Item {item_id} not found")

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict[str, Any]
    ) -> None:
        """
        Delete a specific item from a thread.

        Args:
            thread_id: ID of the thread
            item_id: ID of the item to delete
            context: Request context
        """
        items = self._items(thread_id)
        self._threads[thread_id].items = [item for item in items if item.id != item_id]

    # ==========================================================================
    # FILE ATTACHMENT OPERATIONS
    # ==========================================================================
    # These methods are required by the Store interface but intentionally not
    # implemented in this demo. For production with file uploads, implement
    # these with proper authentication, virus scanning, and storage (S3, etc.)

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict[str, Any],
    ) -> None:
        """
        Save a file attachment.

        NOT IMPLEMENTED in MemoryStore for security reasons.

        Production TODO:
            # 1. Verify user authentication
            # 2. Check file size limits
            # 3. Scan for viruses
            # 4. Store in S3/Azure Blob/GCS
            # 5. Save metadata to database
        """
        raise NotImplementedError(
            "MemoryStore does not persist attachments. Provide a Store implementation "
            "that enforces authentication and authorization before enabling uploads."
        )

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict[str, Any],
    ) -> Attachment:
        """
        Load a file attachment.

        NOT IMPLEMENTED in MemoryStore.

        Production TODO:
            # 1. Verify user has access to this attachment
            # 2. Load from S3/Azure Blob/GCS
            # 3. Return Attachment object
        """
        raise NotImplementedError(
            "MemoryStore does not load attachments. Provide a Store implementation "
            "that enforces authentication and authorization before enabling uploads."
        )

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        """
        Delete a file attachment.

        NOT IMPLEMENTED in MemoryStore.

        Production TODO:
            # 1. Verify user has permission to delete
            # 2. Delete from S3/Azure Blob/GCS
            # 3. Delete metadata from database
        """
        raise NotImplementedError(
            "MemoryStore does not delete attachments because they are never stored."
        )


__all__ = ["MemoryStore"]

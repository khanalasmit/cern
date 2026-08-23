"""Small, bounded conversation memory with optional JSON persistence.

The store deliberately keeps only chat-compatible ``role``/``content``
messages.  It has no dependency on the LLM client and can therefore be used
by the translator, the CLI, or tests independently.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Dict, List, Optional


class ConversationMemory:
    """Store bounded histories independently for each conversation.

    ``max_turns`` is the maximum number of role/content messages retained per
    conversation.  Persistence is opt-in: when ``storage_path`` is omitted,
    data lives only for the lifetime of this instance.  When supplied, the
    store writes an atomic JSON file so a new process can restore the same
    conversation by using the same path and conversation ID.
    """

    _FORMAT_VERSION = 1
    _DEFAULT_CONVERSATION_ID = "default"
    _VALID_ROLES = {"user", "assistant"}

    def __init__(self, storage_path: Optional[os.PathLike | str] = None,
                 max_turns: int = 12):
        if not isinstance(max_turns, int) or isinstance(max_turns, bool) or max_turns < 1:
            raise ValueError("max_turns must be a positive integer")

        self.max_turns = max_turns
        self.storage_path = Path(storage_path).expanduser() if storage_path else None
        self._conversations: Dict[str, List[Dict[str, str]]] = {}
        self._lock = RLock()

        if self.storage_path is not None:
            self._load()

    def add_turn(self, conversation_id: Optional[str], role: str, content: str) -> None:
        """Append one user or assistant message to a conversation."""
        conversation_key = self._conversation_key(conversation_id)
        role = self._validate_role(role)
        content = self._validate_content(content)

        with self._lock:
            messages = list(self._conversations.get(conversation_key, []))
            messages.append({"role": role, "content": content})
            self._store_messages(conversation_key, messages)

    def add_user_turn(self, conversation_id: Optional[str], content: str) -> None:
        """Append a user message."""
        self.add_turn(conversation_id, "user", content)

    def add_assistant_turn(self, conversation_id: Optional[str], content: str) -> None:
        """Append an assistant message."""
        self.add_turn(conversation_id, "assistant", content)

    def add_exchange(self, conversation_id: Optional[str], user_content: str,
                     assistant_content: str) -> None:
        """Append a complete user/assistant exchange in one write operation."""
        conversation_key = self._conversation_key(conversation_id)
        user_content = self._validate_content(user_content)
        assistant_content = self._validate_content(assistant_content)

        with self._lock:
            messages = list(self._conversations.get(conversation_key, []))
            messages.extend([
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content},
            ])
            self._store_messages(conversation_key, messages)

    def get_history(self, conversation_id: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Return a copy of the most recent bounded history messages."""
        conversation_key = self._conversation_key(conversation_id)
        if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit < 0):
            raise ValueError("limit must be a non-negative integer")

        with self._lock:
            messages = self._conversations.get(conversation_key, [])
            if limit is not None:
                messages = messages[-limit:] if limit else []
            return [dict(message) for message in messages]

    def clear(self, conversation_id: Optional[str] = None) -> None:
        """Clear one conversation, defaulting to the default conversation."""
        conversation_key = self._conversation_key(conversation_id)
        with self._lock:
            if conversation_key in self._conversations:
                del self._conversations[conversation_key]
                self._persist()

    def clear_all(self) -> None:
        """Explicitly clear every conversation in this store."""
        with self._lock:
            if self._conversations:
                self._conversations.clear()
                self._persist()

    def _store_messages(self, conversation_key: str,
                        messages: List[Dict[str, str]]) -> None:
        bounded_messages = messages[-self.max_turns:]
        updated = dict(self._conversations)
        updated[conversation_key] = bounded_messages
        self._persist(updated)
        self._conversations = updated

    def _load(self) -> None:
        assert self.storage_path is not None
        if not self.storage_path.exists():
            return

        try:
            with self.storage_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Could not load conversation memory from {self.storage_path}") from exc

        if not isinstance(payload, dict) or payload.get("version") != self._FORMAT_VERSION:
            raise ValueError(f"Unsupported conversation memory format in {self.storage_path}")

        conversations = payload.get("conversations", {})
        if not isinstance(conversations, dict):
            raise ValueError(f"Invalid conversations data in {self.storage_path}")

        loaded: Dict[str, List[Dict[str, str]]] = {}
        for conversation_id, messages in conversations.items():
            if not isinstance(conversation_id, str) or not isinstance(messages, list):
                raise ValueError(f"Invalid conversation memory data in {self.storage_path}")
            validated_messages = []
            for message in messages:
                if not isinstance(message, dict):
                    raise ValueError(f"Invalid conversation memory data in {self.storage_path}")
                role = self._validate_role(message.get("role"))
                content = self._validate_content(message.get("content"))
                validated_messages.append({"role": role, "content": content})
            loaded[conversation_id] = validated_messages[-self.max_turns:]

        self._conversations = loaded

    def _persist(self, conversations: Optional[Dict[str, List[Dict[str, str]]]] = None) -> None:
        if self.storage_path is None:
            return

        data = conversations if conversations is not None else self._conversations
        payload = {"version": self._FORMAT_VERSION, "conversations": data}
        parent = self.storage_path.parent
        parent.mkdir(parents=True, exist_ok=True)

        temporary_path = None
        try:
            file_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.storage_path.name}.",
                dir=str(parent),
                text=True,
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(file_descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self.storage_path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass

    @classmethod
    def _conversation_key(cls, conversation_id: Optional[str]) -> str:
        if conversation_id is None:
            return cls._DEFAULT_CONVERSATION_ID
        if not isinstance(conversation_id, str):
            raise TypeError("conversation_id must be a string or None")
        conversation_key = conversation_id.strip()
        if not conversation_key:
            raise ValueError("conversation_id must not be empty")
        return conversation_key

    @classmethod
    def _validate_role(cls, role: object) -> str:
        if role not in cls._VALID_ROLES:
            raise ValueError("role must be 'user' or 'assistant'")
        return role

    @staticmethod
    def _validate_content(content: object) -> str:
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        return content

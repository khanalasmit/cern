"""llm_compat.py — Compatibility shim for OpenAI-compatible proxies.

Some proxies (e.g. api.cline.bot) wrap the standard ChatCompletion payload
as ``{"data": {"choices": [...]}, "success": true}``. The ``openai`` SDK
then parses top-level ``choices`` as ``None``, so ``response.choices[0]``
raises ``TypeError: 'NoneType' object is not subscriptable`` even though the
call succeeded (HTTP 200).

This helper extracts message content from either shape.
"""

from __future__ import annotations

from typing import Any


def extract_message_content(response: Any) -> str:
    """Return assistant message content from a ChatCompletion response.

    Handles:
      1. Standard OpenAI shape: response.choices[0].message.content
      2. Wrapped proxy shape: response.model_extra["data"]["choices"][0]...
         (also visible via response.model_dump()["data"])
    Raises ValueError when no content is found.
    """
    # 1. Standard shape
    try:
        choices = getattr(response, "choices", None)
        if choices:
            msg = choices[0].message
            content = getattr(msg, "content", None) if not isinstance(msg, dict) else msg.get("content")
            if content:
                return content
    except Exception:
        pass

    # 2. Wrapped shape via model_extra or model_dump
    data = None
    try:
        model_extra = getattr(response, "model_extra", None)
        if isinstance(model_extra, dict) and isinstance(model_extra.get("data"), dict):
            data = model_extra["data"]
    except Exception:
        data = None

    if data is None:
        try:
            dump = response.model_dump() if hasattr(response, "model_dump") else {}
            if isinstance(dump, dict) and isinstance(dump.get("data"), dict):
                data = dump["data"]
        except Exception:
            data = None

    if isinstance(data, dict):
        try:
            wrapped_choices = data.get("choices")
            if wrapped_choices:
                first = wrapped_choices[0]
                if isinstance(first, dict):
                    msg = first.get("message", {})
                    content = msg.get("content") if isinstance(msg, dict) else None
                    if content:
                        return content
                else:
                    msg = getattr(first, "message", None)
                    content = getattr(msg, "content", None) if msg is not None else None
                    if content:
                        return content
        except Exception:
            pass

    raise ValueError("LLM response contained no message content (empty choices and empty data.choices).")

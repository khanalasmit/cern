"""
llm_utils.py — Helper utilities for interacting with LLM providers
===================================================================

Provides common response parsing and normalization to support:
  1. Standard OpenAI Chat Completions API response format.
  2. Enveloped API formats (such as Cline web proxy at api.cline.bot)
     where choices are wrapped inside a top-level {"data": {"choices": [...]}}.
"""
from __future__ import annotations

from typing import Any, Optional


def extract_chat_completion_content(response: Any) -> str:
    """Extract assistant message content from a ChatCompletion response.

    Handles both standard OpenAI API responses and proxy-enveloped responses
    (e.g., api.cline.bot wrapping standard payload in a 'data' dict).

    Parameters
    ----------
    response : Any
        OpenAI ChatCompletion model, dictionary, or mock object.

    Returns
    -------
    str
        Extracted content string (empty string if content cannot be found).
    """
    if response is None:
        return ""

    # 1. Standard OpenAI response object: response.choices[0].message.content
    choices = getattr(response, "choices", None)
    if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
        first = choices[0]
        msg = getattr(first, "message", None)
        if msg is not None:
            content = getattr(msg, "content", None)
            if content is not None:
                return str(content)
        elif isinstance(first, dict):
            msg_dict = first.get("message", {})
            if isinstance(msg_dict, dict):
                return str(msg_dict.get("content", "") or "")

    # 2. Enveloped response in model_extra (e.g. Cline API: {"success": true, "data": {...}})
    extra = getattr(response, "model_extra", None) or {}
    if isinstance(extra, dict):
        data = extra.get("data")
        if isinstance(data, dict):
            env_choices = data.get("choices")
            if env_choices and isinstance(env_choices, (list, tuple)) and len(env_choices) > 0:
                first = env_choices[0]
                if isinstance(first, dict):
                    msg_dict = first.get("message", {})
                    if isinstance(msg_dict, dict):
                        return str(msg_dict.get("content", "") or "")
                msg = getattr(first, "message", None)
                if msg is not None:
                    return str(getattr(msg, "content", "") or "")

    # 3. Direct attribute .data on response
    data = getattr(response, "data", None)
    if isinstance(data, dict):
        env_choices = data.get("choices")
        if env_choices and isinstance(env_choices, (list, tuple)) and len(env_choices) > 0:
            first = env_choices[0]
            if isinstance(first, dict):
                msg_dict = first.get("message", {})
                if isinstance(msg_dict, dict):
                    return str(msg_dict.get("content", "") or "")

    # 4. Dictionary response (e.g. from mocks or raw JSON dict)
    if isinstance(response, dict):
        if "choices" in response and isinstance(response["choices"], (list, tuple)) and response["choices"]:
            first = response["choices"][0]
            if isinstance(first, dict):
                return str(first.get("message", {}).get("content", "") or "")
        if "data" in response and isinstance(response["data"], dict):
            env_choices = response["data"].get("choices")
            if env_choices and isinstance(env_choices, (list, tuple)) and env_choices:
                first = env_choices[0]
                if isinstance(first, dict):
                    return str(first.get("message", {}).get("content", "") or "")

    return ""

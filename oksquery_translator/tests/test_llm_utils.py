"""
test_llm_utils.py — Tests for extract_chat_completion_content
=============================================================

Tests that both standard OpenAI ChatCompletion objects and enveloped
responses (such as those from api.cline.bot) are parsed correctly.
"""
from types import SimpleNamespace
from oksquery_translator.llm_utils import extract_chat_completion_content


def test_extract_standard_openai_object():
    """Test standard response.choices[0].message.content structure."""
    msg = SimpleNamespace(content="Standard assistant response", role="assistant")
    choice = SimpleNamespace(message=msg, index=0)
    response = SimpleNamespace(choices=[choice])

    assert extract_chat_completion_content(response) == "Standard assistant response"


def test_extract_cline_enveloped_model_extra():
    """Test response where choices is None and payload is in model_extra['data']."""
    response = SimpleNamespace(
        choices=None,
        model_extra={
            "success": True,
            "data": {
                "id": "gen-123",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Enveloped Cline response",
                        },
                    }
                ],
            },
        },
    )

    assert extract_chat_completion_content(response) == "Enveloped Cline response"


def test_extract_enveloped_data_attribute():
    """Test response where response.data is a dict containing choices."""
    response = SimpleNamespace(
        choices=None,
        data={
            "choices": [
                {
                    "message": {
                        "content": "Data attr response",
                    }
                }
            ]
        },
    )

    assert extract_chat_completion_content(response) == "Data attr response"


def test_extract_dict_standard():
    """Test raw dictionary in standard OpenAI format."""
    response = {
        "choices": [
            {
                "message": {
                    "content": "Dict standard response",
                }
            }
        ]
    }

    assert extract_chat_completion_content(response) == "Dict standard response"


def test_extract_dict_enveloped():
    """Test raw dictionary in enveloped format."""
    response = {
        "success": True,
        "data": {
            "choices": [
                {
                    "message": {
                        "content": "Dict enveloped response",
                    }
                }
            ]
        },
    }

    assert extract_chat_completion_content(response) == "Dict enveloped response"


def test_extract_empty_or_none():
    """Test None and empty inputs return empty string safely."""
    assert extract_chat_completion_content(None) == ""
    assert extract_chat_completion_content({}) == ""
    assert extract_chat_completion_content(SimpleNamespace(choices=[])) == ""

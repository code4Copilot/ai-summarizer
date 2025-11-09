import os
import sys
import pytest
from types import SimpleNamespace
from unittest.mock import Mock

# Ensure project root is on sys.path so tests can import the top-level modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# If the `openai` package is not installed in the test environment, inject a
# lightweight fake module that provides the `OpenAI` symbol so importing
# `summarizer` won't fail during collection. Tests below will replace or
# monkeypatch the client's methods as needed.
import types
class _DummyOpenAI:
    def __init__(self, api_key=None):
        # client instance will be replaced by mocks in tests
        self.api_key = api_key

sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=_DummyOpenAI))

from summarizer import Summarizer

def test_success_dict_response():
    """
    測試能成功產生摘要（OpenAI 回傳 dict-like 回應）。
    """
    s = Summarizer(api_key="fake-key")
    # 模擬 client 並返回 dict-like response
    mock_client = Mock()
    mock_resp = {"choices": [{"message": {"content": "這是一個測試摘要。"}}]}
    mock_client.chat.completions.create.return_value = mock_resp
    s._client = mock_client
    s._no_key = False

    result = s.summarize("原始文字內容", length="short", language="zh-tw")
    assert result["success"] is True
    assert result["summary"] == "這是一個測試摘要。"

def test_empty_text():
    """
    測試輸入空文字內容會回傳錯誤。
    """
    s = Summarizer(api_key="fake-key")
    # 不需要建立 client，因為驗證在前面就會失敗
    res = s.summarize("", length="short")
    assert res["success"] is False
    assert "text 參數為空" in res["error"]

def test_api_error_handling():
    """
    測試當 OpenAI API 呼叫發生例外時，summarize 會回傳失敗並包含錯誤訊息。
    """
    s = Summarizer(api_key="fake-key")
    mock_client = Mock()
    # 模擬在呼叫時拋出例外
    mock_client.chat.completions.create.side_effect = Exception("API down")
    s._client = mock_client
    s._no_key = False

    res = s.summarize("一些文字", length="short")
    assert res["success"] is False
    assert "摘要生成失敗" in res["error"]
    assert "API down" in res["error"]

def test_success_object_response():
    """
    測試能成功產生摘要（OpenAI 回傳物件式回應，屬性存取的情況）。
    """
    s = Summarizer(api_key="fake-key")
    mock_client = Mock()
    # 建立物件式回傳： resp.choices[0].message.content
    msg = SimpleNamespace(content="物件式回傳的摘要內容。")
    choice = SimpleNamespace(message=msg)
    resp_obj = SimpleNamespace(choices=[choice])
    mock_client.chat.completions.create.return_value = resp_obj
    s._client = mock_client
    s._no_key = False

    res = s.summarize("更多原始文字", length="short", language="zh-tw")
    assert res["success"] is True
    assert res["summary"] == "物件式回傳的摘要內容。"
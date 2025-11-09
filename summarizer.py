import os
import time
from typing import Optional, Union, Dict

from openai import OpenAI

# 嘗試載入本專案的 config（若存在）
try:
    import config
except Exception:
    config = None

class Summarizer:
    """
    簡單的文字摘要器，透過 OpenAI API 產生摘要。
    使用方式：
        s = Summarizer()
        result = s.summarize("要被摘要的文字...", length="short", language="zh-tw")
        if result["success"]:
            print(result["summary"])
        else:
            print("Error:", result["error"])
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", max_retries: int = 2, timeout: int = 30):
        # 使用提供的 api_key，或自 config 或環境變數 OPENAI_API_KEY
        self.api_key = api_key or (getattr(config, "OPENAI_API_KEY", None) if config else None) or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # 不立即拋錯，讓呼叫端可取得統一格式錯誤
            self._no_key = True
        else:
            self._no_key = False
            # 使用新版 openai SDK 的 client 介面
            # OpenAI 物件會使用傳入的 api_key 或環境變數
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                # 若無法建立 client，保留舊行為標記為沒 key，由呼叫端看到錯誤
                self._client = None
                self._no_key = True

        # model 預設：優先傳入，若無則嘗試 config
        self.model = model or (getattr(config, "OPENAI_MODEL_NAME", None) if config else "gpt-3.5-turbo")
        self.max_retries = max_retries
        self.timeout = timeout

    def _length_instruction(self, length: Union[str, int]) -> str:
        # 將 length 轉為對 model 的說明
        if isinstance(length, int) and length > 0:
            return f"請產生約 {length} 字的摘要。"
        if not isinstance(length, str):
            length = "short"
        length = length.lower()
        if length in ("short", "短"):
            return "請以精簡方式摘要成 1~3 句話。"
        if length in ("medium", "中", "中等"):
            return "請以中等長度摘要成 3~6 句話。"
        if length in ("long", "長"):
            return "請以詳細方式摘要，至少 6 句話或更多細節。"
        # fallback
        return "請以簡潔方式摘要成幾句話。"

    def _compute_max_tokens(self, length: Union[str, int]) -> int:
        """
        根據 length（或 config.SUMMARY_LENGTHS）估算要傳給 OpenAI 的 max_tokens。
        簡單假設：1 token 約 4 字元，並加上上下限保護。
        """
        # 若使用整數，視為約字數，估算 token
        if isinstance(length, int) and length > 0:
            tokens = max(64, int(length / 4))
            return min(4096, tokens)

        # 若有 config 定義的 SUMMARY_LENGTHS，嘗試使用
        if config and getattr(config, "SUMMARY_LENGTHS", None):
            key = str(length).lower() if isinstance(length, str) else "medium"
            chars = config.SUMMARY_LENGTHS.get(key, config.SUMMARY_LENGTHS.get("medium", 300))
            return max(64, min(4096, int(chars / 4)))

        # fallback mapping（字數估算）
        mapping = {"short": 100, "medium": 300, "long": 600}
        chars = mapping.get(str(length).lower(), 100)
        return max(64, min(4096, int(chars / 4)))

    def summarize(self, text: str, length: Union[str, int] = "short", language: str = "en") -> Dict[str, Union[bool, str]]:
        """
        產生摘要。
        參數：
         - text: 欲摘要的原文（必填）
         - length: "short"/"medium"/"long" 或 整數（大約字數）
         - language: 要求回傳的語言（例如 "zh-tw", "zh", "en"）
        回傳：
         { "success": True, "summary": "..." } 或 { "success": False, "error": "..." }
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {"success": False, "error": "text 參數為空，請提供要摘要的文字。"}

        if self._no_key:
            return {"success": False, "error": "OpenAI API key 未設定（請設定環境變數 OPENAI_API_KEY 或在建構時傳入 api_key）。"}

        instruction = self._length_instruction(length)
        # 組成 system + user prompt
        system_msg = {
            "role": "system",
            "content": "你是一個專業且客觀的文字摘要工具。"
        }
        user_msg = {
            "role": "user",
            "content": (
                f"{instruction}\n"
                f"請以 {language} 回覆。\n"
                "原文如下：\n"
                f"{text}\n\n"
                "如果原文太短，請直接重述要點；如果有必要，保留重要關鍵字與核心資訊。"
            )
        }

        attempt = 0
        # 計算要給 OpenAI 的 max_tokens
        max_tokens = self._compute_max_tokens(length)
        while attempt <= self.max_retries:
            try:
                # 使用新版 SDK 的呼叫方式
                if not getattr(self, "_client", None):
                    return {"success": False, "error": "OpenAI client 未建立（API key 缺失或無效）。"}

                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[system_msg, user_msg],
                    temperature=0.2,
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                # 取出回覆 - 支援新舊 SDK 的回傳型別（object with attributes 或 dict）
                # 新 SDK: resp.choices -> list of Choice objects with .message.content
                # 舊 SDK: resp is dict-like and supports resp.get("choices")
                choices = None
                if isinstance(resp, dict):
                    choices = resp.get("choices")
                else:
                    # 物件式回傳：嘗試取得 .choices 屬性
                    choices = getattr(resp, "choices", None)

                if not choices:
                    return {"success": False, "error": "OpenAI 回傳空結果。"}

                first = choices[0]
                # message 可能是 dict 或有屬性的物件
                message = None
                if isinstance(first, dict):
                    message = first.get("message", {})
                    summary_text = (message.get("content") or "").strip()
                else:
                    # first may be an object with .message
                    msg_obj = getattr(first, "message", None)
                    if isinstance(msg_obj, dict):
                        summary_text = (msg_obj.get("content") or "").strip()
                    else:
                        # message might be an object with .content
                        summary_text = (getattr(msg_obj, "content", "") or "").strip()

                if not summary_text:
                    return {"success": False, "error": "未從模型取得摘要內容。"}
                return {
                    "success": True,
                    "summary": summary_text,
                    "error": ""
                }
            except Exception as e:
                return {
                    "success": False,
                    "summary": "",
                    "error": f"摘要生成失敗: {str(e)}"
                }

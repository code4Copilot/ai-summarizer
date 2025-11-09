# AI 文本摘要器

簡短說明：這是一個以 OpenAI API 為後端的簡易 AI 文本摘要工具，提供程式介面與 Gradio 範例介面，便於對各種類型文字自動生成摘要。

主要檔案：
- [summarizer.py](summarizer.py) — 內含核心類別：[`Summarizer`](summarizer.py) 與方法 [`Summarizer.summarize`](summarizer.py)。
- [main.py](main.py) — Gradio 範例介面啟動程式。
- [config.py](config.py) — 環境與預設參數讀取、驗證。
- [tests/test_summarizer.py](tests/test_summarizer.py) — pytest 單元測試範例。
- [requirements.txt](requirements.txt) — 相依套件清單。
- [setup_project.bat](setup_project.bat) — Windows 環境建立範例腳本。

功能特色
- 使用 OpenAI（新版 SDK 或舊版 dict 回傳皆支援）產生摘要。
- 支援摘要長度選項：short / medium / long，或以整數指定近似字數。
- 內建簡單重試與錯誤處理邏輯。
- 提供程式 API（[`Summarizer`](summarizer.py)）與 Gradio 線上介面範例（[main.py](main.py)）。
- 含 pytest 範例測試（模擬 OpenAI 回應）。

安裝說明
1. 建議建立虛擬環境並啟用：
```bash
# 在 Unix/macOS
python -m venv .venv
source .venv/bin/activate

# 在 Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. 安裝相依套件：
```bash
pip install -r requirements.txt
```

3. （選用）在 Windows 可執行：
```bat
setup_project.bat
```

使用指南

- 以程式方式呼叫（範例）：
```python
from summarizer import Summarizer

s = Summarizer(api_key="你的_openai_api_key")
res = s.summarize("這是一段需要摘要的文字。", length="short", language="zh-tw")
if res.get("success"):
    print(res["summary"])
else:
    print("錯誤：", res.get("error"))
```
- 使用 Gradio 範例介面：
```bash
python main.py
```
執行後會啟動本機介面，在瀏覽器中輸入文字即可取得摘要。

測試
- 使用 pytest 及 pytest-mock（已在 [tests/test_summarizer.py](tests/test_summarizer.py)）：
```bash
pytest -q
```

環境變數設定
- 必須設定 OpenAI API Key，支援以下方式（優先順序為建構時傳入 > config.py 讀取 > 環境變數）：
  - 在環境變數中設定 OPENAI_API_KEY，例如（Unix/macOS）：
    ```bash
    export OPENAI_API_KEY="你的_openai_api_key"
    ```
  - 或在 Windows PowerShell：
    ```powershell
    $env:OPENAI_API_KEY="你的_openai_api_key"
    ```
  - 也可建立 .env 並使用 [python-dotenv](https://pypi.org/project/python-dotenv/)（config.py 會自動載入）。

- 其他可透過 [config.py](config.py) 調整的設定：
  - OPENAI_MODEL_NAME（預設 "gpt-4o-mini" 或 Summarizer 建構時傳入的 model 參數）
  - MAX_INPUT_LENGTH、SUMMARY_LENGTHS（控制摘要長度估算）
  - GRADIO_SHARE、GRADIO_SERVER_PORT

授權條款
- 本專案預設為 MIT-like 簡單授權（請根據實際需求修改）。若需正式授權，請在本專案根目錄加入 LICENSE 檔案並說明條款。

範例與參考
- 核心實作：[`summarizer.py`](summarizer.py)
- Gradio 範例：[`main.py`](main.py)
- 設定與驗證：[`config.py`](config.py)
- 單元測試範例：[`tests/test_summarizer.py`](tests/test_summarizer.py)

歡迎依需求修改與擴充功能，例如加入更多模型選項、進階錯誤重試策略或本地緩存摘要結果。